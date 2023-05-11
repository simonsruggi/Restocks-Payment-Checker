# Restocks Payment Checker

Restocks Payment Checker is a simple tool designed to check the status of restocks payments. It helps you keep track of the payments you have received.

## Installation

1. Install Python on your system. You can download the latest version of Python from the official Python website: [python.org/downloads](https://www.python.org/downloads/)

2. Clone the repository to your local machine using the following command:
   ```
   git clone https://github.com/your-username/restocks-payment-checker.git
   ```

3. Navigate to the project directory:
   ```
   cd restocks-payment-checker
   ```

4. Install the required dependencies by running the following command in your terminal or command prompt:
   ```
   pip install -r requirements.txt
   ```

5. Save the IDs of the payments you have already received in the `paid_ids.txt` file. You can find these IDs in the emails you received from Wise.

6. Fill in the necessary details in the `.env` file. This file should contain your email and password for the restocks site. Make sure to provide the correct information.

## Usage

Run the following command in your terminal or command prompt to start the Restocks Payment Checker:
```
python3 paymentchecker.py
```

The tool will then check the status of the payments by comparing them with the IDs stored in the `paid_ids.txt` file. You will receive updates and notifications regarding the payment status.

Feel free to modify and adapt the tool according to your specific needs.

Please note that this tool is provided as-is and may require additional customization or modifications based on your environment or specific requirements.

For any issues or questions, please refer to the project repository or contact the project maintainers.

**Disclaimer: Use this tool responsibly and in accordance with the terms of service and policies of the restocks site. Be mindful of privacy and security considerations.**
"

