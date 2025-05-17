#!/usr/bin/env python3
"""
Login Testing Automation Script

This script automates the process of testing login functionality by trying
different combinations of usernames and passwords. It uses the requests
library to send HTTP requests to a login endpoint.
"""

import argparse
import csv
import json
import time
from typing import List, Dict, Union, Tuple
import requests
from requests.exceptions import RequestException
from concurrent.futures import ThreadPoolExecutor, as_completed

class LoginTester:
    """Class to handle automated login testing"""
    
    def __init__(self, 
                 url: str,
                 username_field: str = "username", 
                 password_field: str = "password",
                 success_indicator: str = None,
                 failure_indicator: str = None,
                 headers: Dict = None,
                 timeout: int = 10,
                 delay: float = 0.5,
                 max_workers: int = 5) -> None:
        """
        Initialize the login tester with configuration parameters.
        
        Args:
            url: The login endpoint URL
            username_field: The name of the username form field
            password_field: The name of the password form field
            success_indicator: String that indicates successful login
            failure_indicator: String that indicates failed login
            headers: Custom HTTP headers for requests
            timeout: Request timeout in seconds
            delay: Delay between requests in seconds
            max_workers: Maximum number of concurrent workers
        """
        self.url = url
        self.username_field = username_field
        self.password_field = password_field
        self.success_indicator = success_indicator
        self.failure_indicator = failure_indicator
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        self.timeout = timeout
        self.delay = delay
        self.max_workers = max_workers
        self.results = []
        
    def _is_successful_login(self, response: requests.Response) -> bool:
        """
        Determine if login was successful based on response.
        
        Args:
            response: HTTP response from login attempt
            
        Returns:
            True if login successful, False otherwise
        """
        # Check for success indicator in response
        if self.success_indicator and self.success_indicator in response.text:
            return True
            
        # Check for failure indicator in response
        if self.failure_indicator and self.failure_indicator in response.text:
            return False
            
        # Check HTTP status code (typically 200 for success, 401/403 for failure)
        if response.status_code == 200:
            # Additional checks like redirects or cookies could be added here
            return True
            
        return False
        
    def test_login(self, username: str, password: str) -> Dict:
        """
        Test a single login attempt.
        
        Args:
            username: Username to test
            password: Password to test
            
        Returns:
            Dictionary with login test results
        """
        data = {
            self.username_field: username,
            self.password_field: password
        }
        
        result = {
            "username": username,
            "password": password,
            "success": False,
            "status_code": None,
            "response_time": None,
            "error": None
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                self.url,
                data=data,
                headers=self.headers,
                timeout=self.timeout
            )
            response_time = time.time() - start_time
            
            result.update({
                "status_code": response.status_code,
                "response_time": round(response_time, 3),
                "success": self._is_successful_login(response),
                "response_length": len(response.text)
            })
            
        except RequestException as e:
            result["error"] = str(e)
            
        return result
        
    def run_tests(self, usernames: List[str], passwords: List[str], 
                  parallel: bool = False) -> List[Dict]:
        """
        Run login tests with provided usernames and passwords.
        
        Args:
            usernames: List of usernames to test
            passwords: List of passwords to test
            parallel: Whether to run tests in parallel
            
        Returns:
            List of test results
        """
        test_combinations = [(u, p) for u in usernames for p in passwords]
        total_tests = len(test_combinations)
        print(f"Starting {total_tests} login tests...")
        
        if parallel:
            return self._run_parallel(test_combinations)
        else:
            return self._run_sequential(test_combinations)
    
    def _run_sequential(self, test_combinations: List[Tuple[str, str]]) -> List[Dict]:
        """Run tests sequentially with delay between requests"""
        results = []
        for i, (username, password) in enumerate(test_combinations, 1):
            print(f"Testing {i}/{len(test_combinations)}: {username}:{password}")
            result = self.test_login(username, password)
            results.append(result)
            
            # Print immediate results
            status = "SUCCESS" if result["success"] else "FAILED"
            print(f"  -> {status} (Status: {result['status_code']})")
            
            if i < len(test_combinations):
                time.sleep(self.delay)
                
        return results
    
    def _run_parallel(self, test_combinations: List[Tuple[str, str]]) -> List[Dict]:
        """Run tests in parallel with thread pool"""
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_creds = {
                executor.submit(self.test_login, username, password): (username, password)
                for username, password in test_combinations
            }
            
            for i, future in enumerate(as_completed(future_to_creds), 1):
                username, password = future_to_creds[future]
                print(f"Completed {i}/{len(test_combinations)}: {username}:{password}")
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Print immediate results
                    status = "SUCCESS" if result["success"] else "FAILED"
                    print(f"  -> {status} (Status: {result['status_code']})")
                    
                except Exception as e:
                    print(f"  -> ERROR: {str(e)}")
                    results.append({
                        "username": username,
                        "password": password,
                        "success": False,
                        "error": str(e)
                    })
        
        return results
        
    def save_results(self, results: List[Dict], output_file: str) -> None:
        """
        Save test results to a file.
        
        Args:
            results: List of test results
            output_file: Path to output file
        """
        file_extension = output_file.split('.')[-1].lower()
        
        if file_extension == 'json':
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
        elif file_extension == 'csv':
            if not results:
                print("No results to save")
                return
                
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        print(f"Results saved to {output_file}")
        
    def generate_report(self, results: List[Dict]) -> None:
        """
        Generate and print a summary report of test results.
        
        Args:
            results: List of test results
        """
        if not results:
            print("No results to report")
            return
            
        total = len(results)
        successful = sum(1 for r in results if r.get("success"))
        failed = total - successful
        
        print("\n===== LOGIN TEST REPORT =====")
        print(f"Total tests: {total}")
        print(f"Successful logins: {successful}")
        print(f"Failed logins: {failed}")
        print(f"Success rate: {successful/total*100:.1f}%")
        
        if successful > 0:
            print("\nSuccessful login credentials:")
            for result in results:
                if result.get("success"):
                    print(f"  {result['username']}:{result['password']}")
                    
        print("============================")


def load_credentials_from_file(file_path: str) -> List[str]:
    """
    Load usernames or passwords from a file.
    
    Args:
        file_path: Path to the file containing usernames or passwords
        
    Returns:
        List of strings from the file
    """
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def main():
    parser = argparse.ArgumentParser(description='Automated Login Testing Tool')
    
    # Required arguments
    parser.add_argument('--url', required=True, help='Login endpoint URL')
    
    # Credential sources (direct or from files)
    parser.add_argument('--usernames', nargs='+', help='List of usernames to test')
    parser.add_argument('--passwords', nargs='+', help='List of passwords to test')
    parser.add_argument('--username-file', help='File containing usernames (one per line)')
    parser.add_argument('--password-file', help='File containing passwords (one per line)')
    
    # Login form configuration
    parser.add_argument('--username-field', default='username', help='Username field name')
    parser.add_argument('--password-field', default='password', help='Password field name')
    parser.add_argument('--success-indicator', help='Text indicating successful login')
    parser.add_argument('--failure-indicator', help='Text indicating failed login')
    
    # Testing options
    parser.add_argument('--parallel', action='store_true', help='Run tests in parallel')
    parser.add_argument('--max-workers', type=int, default=5, help='Max parallel workers')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay between requests in seconds')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds')
    
    # Output options
    parser.add_argument('--output', help='Output file for results (json or csv)')
    
    args = parser.parse_args()
    
    # Get usernames
    usernames = []
    if args.usernames:
        usernames.extend(args.usernames)
    if args.username_file:
        usernames.extend(load_credentials_from_file(args.username_file))
    
    # Get passwords
    passwords = []
    if args.passwords:
        passwords.extend(args.passwords)
    if args.password_file:
        passwords.extend(load_credentials_from_file(args.password_file))
    
    if not usernames or not passwords:
        parser.error("You must provide usernames and passwords either directly or through files")
    
    # Create tester and run tests
    tester = LoginTester(
        url=args.url,
        username_field=args.username_field,
        password_field=args.password_field,
        success_indicator=args.success_indicator,
        failure_indicator=args.failure_indicator,
        timeout=args.timeout,
        delay=args.delay,
        max_workers=args.max_workers
    )
    
    # Run the tests
    results = tester.run_tests(usernames, passwords, parallel=args.parallel)
    
    # Generate report
    tester.generate_report(results)
    
    # Save results if output file specified
    if args.output:
        tester.save_results(results, args.output)


if __name__ == "__main__":
    main()
