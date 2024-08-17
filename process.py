#!/usr/bin/env python3

import os
import requests
import concurrent.futures
import threading
import logging

lock = threading.Lock()
global_job_id = 0

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

def check_redirect(host: str):
    job_id = 0  # current job id
    global global_job_id
    with lock:
        global_job_id += 1
        job_id = global_job_id

    if not host:
        logging.error(f'job_id={job_id} Empty host')
        return

    try:
        response = requests.get(f'http://{host}/', allow_redirects=False, timeout=30, headers=headers)
        location = response.headers.get('location', '')
        logging.info(f"job_id={job_id} url=http://{host}/ status_code={response.status_code} location={location}")
        if response.is_redirect and location.lower().startswith('https://'):
            # print(f'{domain} redirects to HTTPS')
            with lock:
                with open('http2https.txt', 'a') as result_file:
                    result_file.write(f"{host}\n")
            return

        response = requests.get(f'https://{host}/', allow_redirects=False, timeout=30, headers=headers)
        location = response.headers.get('location', '')
        logging.info(f"job_id={job_id} url=https://{host}/ status_code={response.status_code} location={location}")
        if response.is_redirect and location.lower().startswith('http://'):
            logging.info(f"job_id={job_id} https://{host}/ redirects to HTTP, ignore.")
            with lock:
                with open('https2http.txt', 'a') as result_file:
                    result_file.write(f"{host}\n")
            return

        with lock:
            with open('result.txt', 'a') as result_file:
                result_file.write(f"{host}\n")
    except requests.RequestException as e:
        logging.error(f'job_id={job_id} RequestException host={host}: : {e}')
    except Exception as e:
        logging.error(f'job_id={job_id} Exception host={host}: {e}')


def setup_logging():
    format='%(asctime)s %(threadName)s:%(thread)d %(levelname)s %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=format,
        handlers=[
            logging.FileHandler('log.log'),
            logging.StreamHandler()
        ]
    )


def main(file_path: str):
    setup_logging()

    if not os.path.exists(file_path):
        logging.error(f'File {file_path} not found')
        return

    logging.info(f"Processing file {file_path}")

    with open(file_path, 'r') as file:
        domains = [line.strip() for line in file]

    max_workers = int(os.environ.get('THREADS', '500'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="worker") as executor:
        executor.map(check_redirect, domains)


if __name__ == '__main__':
    main('extra.txt')
    main('cisco-umbrella-top1m.txt')
