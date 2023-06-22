##############################################################################################
# desc: generate an MFA one-time password compatable with the Aviary two factor authentication
#       exploritory / proof-of-concept code
# usage: python3 experimental/experimental_otp_test.py --otp_key ${opt_key_file}
# license: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
# date: June 22, 2022
##############################################################################################

# Proof-of-concept only
import argparse
import logging
import pyotp


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--logging_level', required=False, help='Logging level.', default=logging.INFO)
    parser.add_argument('--otp_key', required=True, help='File containing the MFA OTP key provided during the MFA setup.')
    return parser.parse_args()


def main():

    args = parse_args()

    with open(args.otp_key, 'r', encoding="utf-8", newline='') as input_file:
        key = input_file.read().rstrip("\n")
        totp = pyotp.TOTP(key)
        print("Current OTP:", totp.now())


if __name__ == "__main__":
    main()
