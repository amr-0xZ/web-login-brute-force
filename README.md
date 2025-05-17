# 🔐 Login-brute

A powerful and flexible Python tool for testing login functionality through automated credential testing. This utility helps security professionals and developers validate authentication systems by testing multiple username and password combinations efficiently.

## ✨ Features

- **Multiple Testing Methods**: Send HTTP requests to test login endpoints systematically
- **Flexible Credential Input**: Use command-line arguments or load from files for large-scale testing
- **Parallel Processing**: Optional multi-threaded testing for significantly faster execution
- **Customizable Parameters**: Configure field names, success/failure indicators, timing, and more
- **Comprehensive Reporting**: Generate detailed test results and save them in JSON or CSV format
- **Rate Limiting Controls**: Built-in delay mechanisms to prevent overloading servers

## 📋 Requirements

- Python 3.6 or higher
- Dependencies listed in `requirements.txt`

## 🚀 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/login-tester.git
   cd web-login-brute-force
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🔧 Usage

Basic usage example:

```bash
python login-brute.py --url "https://example.com/login" --usernames admin user --passwords pass1234 pass5678
```

### Command-line Arguments

| Argument | Description |
|----------|-------------|
| `--url` | Login endpoint URL (**required**) |
| `--usernames` | Space-separated list of usernames to test |
| `--passwords` | Space-separated list of passwords to test |
| `--username-file` | File containing usernames (one per line) |
| `--password-file` | File containing passwords (one per line) |
| `--username-field` | Name of username form field (default: "username") |
| `--password-field` | Name of password form field (default: "password") |
| `--success-indicator` | Text string indicating successful login |
| `--failure-indicator` | Text string indicating failed login |
| `--parallel` | Enable parallel testing |
| `--max-workers` | Maximum number of parallel workers (default: 5) |
| `--delay` | Delay between requests in seconds (default: 0.5) |
| `--timeout` | Request timeout in seconds (default: 10) |
| `--output` | Output file for results (JSON or CSV format) |

## 📝 Examples

### Testing with credential files:
```bash
python login-brute.py --url "https://example.com/login" --username-file usernames.txt --password-file passwords.txt --output results.json
```

### Testing with custom form field names:
```bash
python login-brute.py --url "https://example.com/login" --usernames admin --passwords test123 --username-field "user_id" --password-field "user_pass"
```

### Fast parallel testing:
```bash
python login-brute.py --url "https://example.com/login" --username-file users.txt --password-file passwords.txt --parallel --max-workers 10 --delay 0.2
```

### Custom success/failure detection:
```bash
python login-brute.py --url "https://example.com/login" --usernames admin --passwords password123 --success-indicator "Welcome back" --failure-indicator "Invalid credentials"
```

## 📊 Sample Output

When running the tool, you'll see real-time progress:

```
Starting 12 login tests...
Testing 1/12: admin:password123
  -> FAILED (Status: 401)
Testing 2/12: admin:welcome12345
  -> SUCCESS (Status: 200)
...

===== LOGIN TEST REPORT =====
Total tests: 12
Successful logins: 1
Failed logins: 11
Success rate: 8.3%

Successful login credentials:
  admin:welcome12345
============================
```
