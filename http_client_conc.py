#!/usr/bin/env python3
"""
Concurrent HTTP Client - Homework 4
Python-based HTTP client for performance testing.
Can download URLs sequentially or concurrently.

Usage:
    python3 http_client_conc.py -u <url> -o <output_file>
    python3 http_client_conc.py -f <url_file> -c <num_connections> -o <output_dir>
    python3 http_client_conc.py -f <url_file> -sequential -o <output_dir>

TODO FOR TEAMMATE 1:
- This client is provided as a Python alternative to the C client from HW2
- You can use this for Part 1 performance evaluation, or adapt your HW2 C client
- Tasks:
  1. Download testscript1.txt and testscript2.txt from the course website
  2. Run sequential downloads for both test scripts
  3. Run concurrent downloads (10 connections) for both test scripts
  4. Calculate and document speedup for each test script
  5. Update README.txt with Part 1 results and analysis
  6. Test the client with various scenarios to ensure reliability

"""

import socket
import argparse
import sys
import time
import threading
import os
from urllib.parse import urlparse
from typing import List, Tuple
import queue


def parse_url(url: str) -> Tuple[str, str, int, str]:
    """
    Parse URL into components.
    
    Args:
        url: URL string
        
    Returns:
        Tuple of (hostname, path, port, scheme)
    """
    parsed = urlparse(url)
    
    hostname = parsed.hostname
    if not hostname:
        raise ValueError(f"Invalid URL: {url}")
    
    path = parsed.path or '/'
    if parsed.query:
        path += '?' + parsed.query
    
    port = parsed.port
    if not port:
        port = 80 if parsed.scheme == 'http' else 443
    
    scheme = parsed.scheme or 'http'
    
    return (hostname, path, port, scheme)


def download_file(url: str, output_path: str = None, verbose: bool = False) -> Tuple[bool, float, int]:
    """
    Download a single file from URL.
    
    Args:
        url: URL to download
        output_path: Path to save file (optional, uses filename from URL)
        verbose: Print progress information
        
    Returns:
        Tuple of (success, download_time, file_size)
    """
    try:
        start_time = time.time()
        
        # Parse URL
        hostname, path, port, scheme = parse_url(url)
        
        if scheme != 'http':
            print(f"Error: Only HTTP is supported (not {scheme})", file=sys.stderr)
            return (False, 0, 0)
        
        # Create socket connection
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(30)  # 30 second timeout
        
        try:
            client_socket.connect((hostname, port))
            
            # Send HTTP GET request
            request = f"GET {path} HTTP/1.1\r\n"
            request += f"Host: {hostname}\r\n"
            request += "Connection: close\r\n"
            request += "\r\n"
            
            client_socket.sendall(request.encode('utf-8'))
            
            # Receive response
            response_data = b''
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                response_data += chunk
            
            # Parse response
            response_str = response_data.decode('utf-8', errors='ignore')
            header_end = response_str.find('\r\n\r\n')
            
            if header_end == -1:
                print(f"Error: Invalid response from {url}", file=sys.stderr)
                return (False, 0, 0)
            
            headers = response_str[:header_end]
            body = response_data[header_end + 4:]
            
            # Check status code
            status_line = headers.split('\r\n')[0]
            if not status_line.startswith('HTTP/1.'):
                print(f"Error: Invalid HTTP response from {url}", file=sys.stderr)
                return (False, 0, 0)
            
            status_code = int(status_line.split()[1])
            
            if status_code != 200:
                print(f"Error: HTTP {status_code} from {url}", file=sys.stderr)
                return (False, 0, 0)
            
            # Determine output path
            if not output_path:
                # Extract filename from URL
                filename = os.path.basename(path)
                if not filename or filename == '/':
                    filename = 'index.html'
                output_path = filename
            
            # Save file
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(body)
            
            download_time = time.time() - start_time
            file_size = len(body)
            
            if verbose:
                print(f"Downloaded {url} -> {output_path} ({file_size} bytes, {download_time:.2f}s)")
            
            return (True, download_time, file_size)
            
        finally:
            client_socket.close()
            
    except Exception as e:
        print(f"Error downloading {url}: {e}", file=sys.stderr)
        return (False, 0, 0)


def download_worker(url_queue: queue.Queue, output_dir: str, results: List, verbose: bool):
    """Worker thread for concurrent downloads."""
    while True:
        try:
            url = url_queue.get(timeout=1)
            if url is None:
                break
            
            # Generate output filename
            filename = os.path.basename(urlparse(url).path)
            if not filename or filename == '/':
                filename = f"file_{hash(url) % 10000}.html"
            
            output_path = os.path.join(output_dir, filename) if output_dir else filename
            
            success, elapsed, size = download_file(url, output_path, verbose)
            results.append((url, success, elapsed, size))
            
            url_queue.task_done()
        except queue.Empty:
            break
        except Exception as e:
            print(f"Worker error: {e}", file=sys.stderr)
            url_queue.task_done()


def download_concurrent(urls: List[str], num_connections: int, output_dir: str = None, verbose: bool = False) -> Tuple[float, List]:
    """
    Download multiple URLs concurrently.
    
    Args:
        urls: List of URLs to download
        num_connections: Number of concurrent connections
        output_dir: Directory to save files
        verbose: Print progress information
        
    Returns:
        Tuple of (total_time, results_list)
    
    TODO FOR TEAMMATE 1:
    - Verify this function works correctly with the test scripts
    - Check that timing measurements are accurate
    - Ensure proper error handling for failed downloads
    - Consider adding retry logic for transient network errors
    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    url_queue = queue.Queue()
    for url in urls:
        url_queue.put(url)
    
    results = []
    threads = []
    
    start_time = time.time()
    
    # Create worker threads
    for _ in range(min(num_connections, len(urls))):
        thread = threading.Thread(
            target=download_worker,
            args=(url_queue, output_dir, results, verbose)
        )
        thread.start()
        threads.append(thread)
    
    # Wait for all downloads to complete
    url_queue.join()
    
    # Signal threads to stop
    for _ in threads:
        url_queue.put(None)
    
    for thread in threads:
        thread.join()
    
    total_time = time.time() - start_time
    
    return (total_time, results)


def download_sequential(urls: List[str], output_dir: str = None, verbose: bool = False) -> Tuple[float, List]:
    """
    Download multiple URLs sequentially.
    
    Args:
        urls: List of URLs to download
        output_dir: Directory to save files
        verbose: Print progress information
        
    Returns:
        Tuple of (total_time, results_list)
    """
    results = []
    start_time = time.time()
    
    for i, url in enumerate(urls):
        # Generate output filename
        filename = os.path.basename(urlparse(url).path)
        if not filename or filename == '/':
            filename = f"file_{i}.html"
        
        output_path = os.path.join(output_dir, filename) if output_dir else filename
        
        success, elapsed, size = download_file(url, output_path, verbose)
        results.append((url, success, elapsed, size))
    
    total_time = time.time() - start_time
    
    return (total_time, results)


def read_urls_from_file(filepath: str) -> List[str]:
    """Read URLs from a text file (one URL per line)."""
    urls = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)
    except Exception as e:
        print(f"Error reading URL file {filepath}: {e}", file=sys.stderr)
        sys.exit(1)
    
    return urls


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='HTTP Client for concurrent/sequential downloads',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-u', '--url', type=str,
                       help='Single URL to download')
    parser.add_argument('-f', '--file', type=str,
                       help='File containing URLs (one per line)')
    parser.add_argument('-o', '--output', type=str,
                       help='Output file or directory')
    parser.add_argument('-c', '--concurrent', type=int, default=10,
                       help='Number of concurrent connections (default: 10)')
    parser.add_argument('-sequential', action='store_true',
                       help='Download sequentially instead of concurrently')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.url and not args.file:
        print("Error: Must specify either -u (URL) or -f (file)", file=sys.stderr)
        sys.exit(1)
    
    if args.url and args.file:
        print("Error: Cannot specify both -u and -f", file=sys.stderr)
        sys.exit(1)
    
    # Single URL download
    if args.url:
        success, elapsed, size = download_file(args.url, args.output, args.verbose)
        if success:
            print(f"Downloaded {size} bytes in {elapsed:.2f} seconds")
            sys.exit(0)
        else:
            sys.exit(1)
    
    # Multiple URL download
    urls = read_urls_from_file(args.file)
    if not urls:
        print("Error: No URLs found in file", file=sys.stderr)
        sys.exit(1)
    
    if args.sequential:
        total_time, results = download_sequential(urls, args.output, args.verbose)
        mode = "Sequential"
    else:
        total_time, results = download_concurrent(urls, args.concurrent, args.output, args.verbose)
        mode = f"Concurrent ({args.concurrent} connections)"
    
    # Print summary
    successful = sum(1 for _, success, _, _ in results if success)
    total_size = sum(size for _, _, _, size in results if success)
    
    print(f"\n{mode} Download Summary:")
    print(f"  Total URLs: {len(urls)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {len(urls) - successful}")
    print(f"  Total time: {total_time:.2f} seconds")
    print(f"  Total size: {total_size} bytes")
    if successful > 0:
        print(f"  Average speed: {total_size / total_time / 1024:.2f} KB/s")


if __name__ == '__main__':
    main()

