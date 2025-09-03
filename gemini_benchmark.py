#!/usr/bin/env python3
"""
Gemini API Benchmark for Polish Law LLM Testing

This script uses Google's free Gemini API to test language models on Polish law exams.
Supports batch processing, rate limiting, and resumable processing.
"""

import os
import json
import time
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import google.generativeai as genai
from tqdm import tqdm
import sys

# Import functions from parser
from parser import load_jsonl, save_as_jsonl

class GeminiBenchmark:
    """Benchmark runner for testing Gemini models on Polish law exams."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        """
        Initialize the benchmark runner.
        
        Args:
            api_key: Google API key for Gemini. If None, reads from GEMINI_API_KEY env var
            model_name: Name of the Gemini model to use
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("API key required. Set GEMINI_API_KEY environment variable or pass api_key parameter")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        
        # Rate limiting settings (free tier: 15 RPM, 1M TPM, 1500 RPD)
        self.requests_per_minute = 15
        self.min_delay_between_requests = 60.0 / self.requests_per_minute
        self.last_request_time = 0
        
    def format_question_prompt(self, question: Dict) -> str:
        """
        Format a question for the Gemini API.
        
        Args:
            question: Question dictionary with question text and options
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Jesteś ekspertem w prawie polskim biorącym udział w egzaminie testowym. 
Odpowiedz na poniższe pytanie wybierając TYLKO jedną prawidłową odpowiedź (A, B lub C).

Pytanie {question['question_number']}:
{question['question']}

A. {question['A']}
B. {question['B']}
C. {question['C']}

Instrukcje:
1. Przeanalizuj dokładnie pytanie i wszystkie opcje
2. Wybierz najbardziej prawidłową odpowiedź zgodnie z polskim prawem
3. Odpowiedz TYLKO literą: A, B lub C
4. NIE dodawaj żadnego wyjaśnienia ani dodatkowego tekstu

Twoja odpowiedź:"""
        return prompt
    
    def rate_limit_wait(self):
        """Wait if necessary to respect rate limits."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_delay_between_requests:
            sleep_time = self.min_delay_between_requests - time_since_last_request
            time.sleep(sleep_time)
    
    def get_model_answer(self, question: Dict, max_retries: int = 3) -> Tuple[str, Optional[str]]:
        """
        Get model's answer for a single question.
        
        Args:
            question: Question dictionary
            max_retries: Maximum number of retries on error
            
        Returns:
            Tuple of (answer, error_message)
        """
        prompt = self.format_question_prompt(question)
        
        for attempt in range(max_retries):
            try:
                # Rate limiting
                self.rate_limit_wait()
                
                # Generate response
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,  # Low temperature for more deterministic answers
                        max_output_tokens=10,  # We only need a single letter
                    )
                )
                self.last_request_time = time.time()
                
                # Extract answer
                answer_text = response.text.strip().upper()
                
                # Validate answer
                if answer_text in ['A', 'B', 'C']:
                    return answer_text, None
                elif len(answer_text) > 0:
                    # Try to extract just the letter if model added extra text
                    for letter in ['A', 'B', 'C']:
                        if letter in answer_text[:3]:  # Check first 3 characters
                            return letter, None
                
                # Invalid format
                return answer_text[:10], f"Invalid answer format: {answer_text[:50]}"
                
            except Exception as e:
                error_msg = f"Attempt {attempt + 1} failed: {str(e)}"
                if attempt == max_retries - 1:
                    return "", error_msg
                
                # Exponential backoff
                time.sleep(2 ** attempt)
        
        return "", "Max retries exceeded"
    
    def run_benchmark(self, questions_file: str, answers_file: Optional[str] = None,
                     output_file: Optional[str] = None, resume_from: int = 0) -> Dict:
        """
        Run benchmark on a set of questions.
        
        Args:
            questions_file: Path to questions file (JSON or JSONL)
            answers_file: Optional path to answers file for evaluation
            output_file: Optional path to save results
            resume_from: Question number to resume from (for interrupted runs)
            
        Returns:
            Dictionary with results and statistics
        """
        # Load questions
        if questions_file.endswith('.jsonl'):
            questions = load_jsonl(questions_file)
        else:
            with open(questions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                questions = data.get('questions', data if isinstance(data, list) else [])
        
        # Load answers if provided
        correct_answers = {}
        if answers_file:
            if answers_file.endswith('.jsonl'):
                answers = load_jsonl(answers_file)
            else:
                with open(answers_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    answers = data.get('answers', data if isinstance(data, list) else [])
            
            correct_answers = {a['question_number']: a['correct_answer'] for a in answers}
        
        # Prepare results structure
        results = {
            'model_name': self.model_name,
            'questions_file': questions_file,
            'timestamp': datetime.now().isoformat(),
            'total_questions': len(questions),
            'responses': [],
            'statistics': {}
        }
        
        # Load existing results if resuming
        existing_responses = {}
        if output_file and os.path.exists(output_file) and resume_from > 0:
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    for resp in existing_data.get('responses', []):
                        existing_responses[resp['question_number']] = resp
                print(f"Resuming from question {resume_from}, loaded {len(existing_responses)} existing responses")
            except Exception as e:
                print(f"Warning: Could not load existing results: {e}")
        
        # Process questions
        correct_count = 0
        error_count = 0
        
        print(f"Testing {len(questions)} questions with {self.model_name}")
        print(f"Rate limit: {self.requests_per_minute} requests per minute")
        
        for question in tqdm(questions, desc="Processing questions"):
            q_num = question['question_number']
            
            # Skip if already processed
            if q_num in existing_responses:
                response = existing_responses[q_num]
                results['responses'].append(response)
                if response['is_correct']:
                    correct_count += 1
                if response.get('error'):
                    error_count += 1
                continue
            
            # Skip if before resume point
            if q_num < resume_from:
                continue
            
            # Get model answer
            model_answer, error = self.get_model_answer(question)
            
            # Prepare response record
            response = {
                'question_number': q_num,
                'model_answer': model_answer,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add correct answer and evaluation if available
            if q_num in correct_answers:
                response['correct_answer'] = correct_answers[q_num]
                response['is_correct'] = model_answer == correct_answers[q_num]
                if response['is_correct']:
                    correct_count += 1
            else:
                response['is_correct'] = None
            
            # Add error if any
            if error:
                response['error'] = error
                error_count += 1
            
            results['responses'].append(response)
            
            # Save intermediate results periodically
            if output_file and len(results['responses']) % 10 == 0:
                self.save_results(results, output_file)
        
        # Calculate statistics
        results['statistics'] = {
            'total_processed': len(results['responses']),
            'correct_answers': correct_count,
            'incorrect_answers': len(results['responses']) - correct_count - error_count,
            'errors': error_count,
            'accuracy': correct_count / len(results['responses']) if results['responses'] else 0,
            'completion_rate': len(results['responses']) / len(questions) if questions else 0
        }
        
        # Save final results
        if output_file:
            self.save_results(results, output_file)
            print(f"\nResults saved to {output_file}")
        
        # Print summary
        print(f"\nBenchmark completed!")
        print(f"Total questions: {len(questions)}")
        print(f"Processed: {results['statistics']['total_processed']}")
        if correct_answers:
            print(f"Correct: {correct_count} ({results['statistics']['accuracy']:.1%})")
            print(f"Incorrect: {results['statistics']['incorrect_answers']}")
        print(f"Errors: {error_count}")
        
        return results
    
    def save_results(self, results: Dict, output_file: str):
        """Save results to file."""
        # Save as JSON with pretty printing
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Also save responses as JSONL for easy processing
        jsonl_file = output_file.replace('.json', '_responses.jsonl')
        save_as_jsonl(results['responses'], jsonl_file)
    
    def analyze_errors(self, results: Dict) -> Dict:
        """
        Analyze error patterns in results.
        
        Args:
            results: Results dictionary from run_benchmark
            
        Returns:
            Dictionary with error analysis
        """
        analysis = {
            'error_types': {},
            'incorrect_patterns': {},
            'question_numbers_with_errors': []
        }
        
        for response in results['responses']:
            if response.get('error'):
                error_type = response['error'].split(':')[0]
                analysis['error_types'][error_type] = analysis['error_types'].get(error_type, 0) + 1
                analysis['question_numbers_with_errors'].append(response['question_number'])
            
            if response.get('is_correct') == False:
                pattern = f"{response.get('correct_answer', '?')} -> {response['model_answer']}"
                analysis['incorrect_patterns'][pattern] = analysis['incorrect_patterns'].get(pattern, 0) + 1
        
        return analysis


def main():
    """Main entry point for the benchmark script."""
    parser = argparse.ArgumentParser(
        description='Run Gemini benchmark on Polish law exams',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test on a single exam with answers
  python gemini_benchmark.py exams/2024/adwokacki_radcowy/questions.json \\
      --answers exams/2024/adwokacki_radcowy/answers.json \\
      --output results/gemini_adwokacki_2024.json

  # Test without answers (just generate responses)
  python gemini_benchmark.py exams/2024/komorniczy/questions.json \\
      --output results/gemini_komorniczy_2024.json

  # Resume from question 50 after interruption
  python gemini_benchmark.py exams/2024/notarialny/questions.json \\
      --resume 50 --output results/gemini_notarialny_2024.json

  # Use a different Gemini model
  python gemini_benchmark.py exams/2024/adwokacki_radcowy/questions.json \\
      --model gemini-1.5-pro --output results/gemini_pro_test.json
        """
    )
    
    parser.add_argument('questions', help='Path to questions file (JSON or JSONL)')
    parser.add_argument('--answers', help='Path to answers file for evaluation')
    parser.add_argument('--output', help='Path to save results')
    parser.add_argument('--model', default='gemini-1.5-flash', 
                       help='Gemini model name (default: gemini-1.5-flash)')
    parser.add_argument('--api-key', help='Google API key (or set GEMINI_API_KEY env var)')
    parser.add_argument('--resume', type=int, default=0,
                       help='Resume from question number (for interrupted runs)')
    parser.add_argument('--analyze', action='store_true',
                       help='Perform error analysis after benchmark')
    
    args = parser.parse_args()
    
    # Check if questions file exists
    if not os.path.exists(args.questions):
        print(f"Error: Questions file not found: {args.questions}")
        sys.exit(1)
    
    # Check if answers file exists (if provided)
    if args.answers and not os.path.exists(args.answers):
        print(f"Error: Answers file not found: {args.answers}")
        sys.exit(1)
    
    try:
        # Initialize benchmark runner
        benchmark = GeminiBenchmark(api_key=args.api_key, model_name=args.model)
        
        # Run benchmark
        results = benchmark.run_benchmark(
            questions_file=args.questions,
            answers_file=args.answers,
            output_file=args.output,
            resume_from=args.resume
        )
        
        # Analyze errors if requested
        if args.analyze and results['statistics']['errors'] > 0:
            print("\nError Analysis:")
            analysis = benchmark.analyze_errors(results)
            print(f"Error types: {analysis['error_types']}")
            print(f"Incorrect patterns: {analysis['incorrect_patterns']}")
            
            # Save analysis
            if args.output:
                analysis_file = args.output.replace('.json', '_analysis.json')
                with open(analysis_file, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, ensure_ascii=False, indent=2)
                print(f"Analysis saved to {analysis_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()