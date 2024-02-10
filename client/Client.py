import socket
import time
from typing import Callable
import requests
import json
from typing import Tuple
from retry import retry
from concurrent.futures import ThreadPoolExecutor

TIME_BETWEEN_PULLS = 1

class Client:
    def __init__(self, host: str, port: int, max_worker_threads: int = 1) -> None:
        self.socket = socket.socket()
        self.socket.connect((host, port))
        self.sequence_number = 0
        self.producer_id = int(round(time.time() * 1000))  # Todo: server should determine pID
        self.thread_pool = ThreadPoolExecutor(max_workers=max_worker_threads)
        return

    def push(self, key: str, value: bytes) -> str:
        self.sequence_number += 1
        # url = f"http://{self.host}:{self.port}/queue/push"
        url = "http://127.0.0.1:5000/queue/push"
        data = {'key': key, 'value': value.decode(), 'sequence_number': self.sequence_number, 'producer_id': self.producer_id}
        headers = {'Content-Type': 'application/json'}
        json_data = json.dumps(data)
        try:
            response = requests.post(url, data=json_data, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

    def pull(self) -> Tuple[str, bytes]:
        # url = f"http://{self.host}:{self.port}/health"
        url = "http://127.0.0.1:5000/queue/pull"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return str(response.status_code), response.content
        except requests.exceptions.RequestException as e:
            return str(e), b''

    def subscribe(self, f: Callable[[str, bytes], None]) -> None:
        self.thread_pool.submit(self.consumer_function, args=(f))
        return

    def consumer_function(self, f: Callable[[str, bytes], None]) -> None:
        while(True):
            time.sleep(TIME_BETWEEN_PULLS)
            key, value = self.pull()
            f(key, value)
        return

    @retry(requests.exceptions.RequestException, tries=5, delay=2, backoff=2)
    def send_ack(self, producer_id: int, sequence_number: int) -> None:
        url = "http://127.0.0.1:5000/queue/ack"
        try:
            data = {'producer_id': producer_id, 'sequence_number': sequence_number}
            headers = {'Content-Type': 'application/json'}
            json_data = json.dumps(data)
            response = requests.post(url, data=json_data, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return str(e), b''


