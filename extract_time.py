import re


for file_name in ['log1.txt', 'log2.txt']:
    # Sample log data (replace this with the actual full log string)
    with open(file_name, "r") as f:
        log_data = f.read()

    # Regular expression to extract lines like "X solved in Y seconds" or "X unsolved in Y seconds"
    pattern = re.compile(r"(\d+)\s+(solved|unsolved)\s+in\s+([0-9.]+)\s+seconds")

    # Extract matches
    matches = pattern.findall(log_data)

    results = [(int(problem_id), float(time)) for problem_id, _, time in matches]

    sorted_by_id = sorted(results, key=lambda x: x[0])

    total_time = sum(time for _, time in sorted_by_id)
    average_time = total_time / len(sorted_by_id)

    print('avg:', average_time)

    solved_times = [float(time) for _, status, time in matches if status == "solved"]
    unsolved_times = [float(time) for _, status, time in matches if status == "unsolved"]

    # Compute averages
    avg_solved_time = sum(solved_times) / len(solved_times) if solved_times else 0
    avg_unsolved_time = sum(unsolved_times) / len(unsolved_times) if unsolved_times else 0

    print('solved', len(solved_times), avg_solved_time)
    print('unsolved', len(unsolved_times), avg_unsolved_time)



# # Sample log data (replace this with the actual full log string)
# with open('log1.txt', "r") as f:
#     log_data = f.read()

# # Regular expression to extract lines like "X solved in Y seconds" or "X unsolved in Y seconds"
# pattern = re.compile(r"(\d+)\s+(solved|unsolved)\s+in\s+([0-9.]+)\s+seconds")

# # Extract matches
# matches = pattern.findall(log_data)

# results = [(int(problem_id), float(time)) for problem_id, _, time in matches]


# solved1 = [_ for _, status, time in matches if status == "solved"]

# with open('log2.txt', "r") as f:
#     log_data = f.read()

# # Regular expression to extract lines like "X solved in Y seconds" or "X unsolved in Y seconds"
# pattern = re.compile(r"(\d+)\s+(solved|unsolved)\s+in\s+([0-9.]+)\s+seconds")

# # Extract matches
# matches = pattern.findall(log_data)

# results = [(int(problem_id), float(time)) for problem_id, _, time in matches]


# solved2 = [_ for _, status, time in matches if status == "solved"]

# for i in solved1:
#     if i not in solved2:
#         print(i)