# Team Notes and Task Distribution

## Project Overview
Homework 4: Concurrent Connection HTTP Server
- Server implementation: Hugo Padilla
- Client and Part 1 testing: [Teammate 1]
- Part 2 testing and validation: [Teammate 2]

## Completed

### Server Implementation (http_server_conc.py)
- ✅ Concurrent HTTP server with threading support
- ✅ Command-line argument parsing (-p, -maxclient, -maxtotal)
- ✅ Per-client connection limit enforcement
- ✅ System-wide connection limit enforcement
- ✅ Thread-safe connection tracking
- ✅ HTTP request parsing and response generation
- ✅ Error handling (404, 500, 503)
- ✅ File serving with proper MIME types

### Supporting Files
- ✅ HTTP client (http_client_conc.py) - Python alternative to C client
- ✅ README.txt with assignment questions answered

## Tasks for Teammate 1

### Part 1: External Downloads Performance Evaluation

**Objective:** Measure speedup from concurrent downloads using external URLs.

**Steps:**
1. Download test scripts:
   - `https://zechuncao.com/teaching/csci4406/testfiles/testscript1.txt`
   - `https://zechuncao.com/teaching/csci4406/testfiles/testscript2.txt`

2. Extract URLs from each test script (one URL per line).

3. Run sequential downloads:
   ```bash
   python3 http_client_conc.py -f testscript1.txt -sequential -o seq_output1 -v
   python3 http_client_conc.py -f testscript2.txt -sequential -o seq_output2 -v
   ```
   Record the total time for each.

4. Run concurrent downloads (10 connections):
   ```bash
   python3 http_client_conc.py -f testscript1.txt -c 10 -o conc_output1 -v
   python3 http_client_conc.py -f testscript2.txt -c 10 -o conc_output2 -v
   ```
   Record the total time for each.

5. Calculate speedup:
   - Speedup = Time_Sequential / Time_Concurrent
   - Document results in README.txt (Section 12: Performance Results, Part 1)

6. Analysis:
   - Explain factors affecting speedup
   - Compare results between testscript1 and testscript2
   - Note any issues or anomalies

**Alternative:** If you prefer using the C client from HW2, you'll need to:
- Modify it to support concurrent downloads, OR
- Run multiple instances and aggregate results

**Files to update:**
- README.txt (Section 12 - Part 1 results)
- Test results and timing data

## Tasks for Teammate 2

### Part 2: Local Server Performance Evaluation

**Objective:** Measure speedup from concurrent downloads using our local server.

**Steps:**
1. Obtain test files:
   - `testfiles1.tar.gz`
   - `testfiles2.tar.gz`
   Place these files in the same directory as the server.

2. Start the server:
   ```bash
   python3 http_server_conc.py -p 20001 -maxclient 12 -maxtotal 60
   ```
   Keep the server running in one terminal.

3. For each test file (testfiles1.tar.gz and testfiles2.tar.gz):
   
   a. Sequential download:
      ```bash
      time python3 http_client_conc.py -u http://localhost:20001/testfiles1.tar.gz -o test1_seq.tar.gz -v
      ```
      Record the time.
   
   b. Concurrent download (10 connections):
      Note: For single file, you may need to:
      - Create a URL list file with the same URL repeated 10 times, OR
      - Modify the client to support chunked concurrent downloads, OR
      - Use multiple processes/threads manually
      
      If using URL list approach:
      ```bash
      # Create test1_urls.txt with 10 lines of the same URL
      python3 http_client_conc.py -f test1_urls.txt -c 10 -o test1_conc -v
      ```
      Record the time.

4. Calculate speedup for each test file:
   - Speedup = Time_Sequential / Time_Concurrent
   - Document results in README.txt (Section 12: Performance Results, Part 2)

5. Additional testing:
   - Test with different connection limits
   - Verify connection limits are enforced correctly
   - Test error handling (404, connection limits)
   - Verify server stability under load

6. Analysis:
   - Compare Part 2 results with Part 1
   - Explain why local server might show different speedup
   - Document any issues or observations

**Files to update:**
- README.txt (Section 12 - Part 2 results)
- Test results and timing data

## Testing Checklist

### Both Teammates Should Verify:

- [ ] Server compiles and runs on bayou
- [ ] Server accepts correct command-line arguments
- [ ] Connection limits are enforced correctly
- [ ] Server handles multiple concurrent connections
- [ ] Server serves files correctly
- [ ] Server returns proper error codes (404, 503)
- [ ] Client can download files sequentially
- [ ] Client can download files concurrently
- [ ] Performance tests run successfully
- [ ] Results are documented in README.txt

## Code Review Notes

### For Teammate 1 (Client):
- Review http_client_conc.py for any issues
- Test with various URL formats and file sizes
- Verify timing accuracy
- Consider adding retry logic for failed downloads
- Check error handling for network issues

### For Teammate 2 (Server Testing):
- Test server with various connection limit configurations
- Verify thread safety under high load
- Test edge cases (max connections, invalid requests)
- Verify proper cleanup when connections close
- Check server logs for any errors

## Important Notes

1. **Compilation on bayou:**
   - Server is Python, no compilation needed
   - Make sure Python 3 is available: `python3 --version`
   - Make executable: `chmod +x http_server_conc.py`

2. **File locations:**
   - Server should be in the same directory as files to serve
   - Test files (testfiles1.tar.gz, testfiles2.tar.gz) must be accessible

3. **Performance testing:**
   - Run tests multiple times for accuracy
   - Note network conditions and system load
   - Document any anomalies

4. **Documentation:**
   - All results must be in README.txt
   - Include analysis and explanations
   - Note any issues or limitations

## Questions or Issues?

If you encounter any problems:
1. Check the code comments for implementation details
2. Review README.txt for explanations
3. Test individual components separately
4. Check server logs for error messages
5. Verify all dependencies are available

Good luck with your parts!

