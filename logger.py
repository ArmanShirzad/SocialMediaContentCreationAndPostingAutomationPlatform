import os
from datetime import datetime

def log_to_file(filename, **variables):
    """
    Log variables to a file with timestamp
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_dir = "logs"
    
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    filepath = os.path.join(log_dir, filename)
    
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"{'='*50}\n")
        
        for var_name, var_value in variables.items():
            f.write(f"\n{var_name}:\n")
            f.write(f"{'-'*50}\n")
            f.write(f"{var_value}\n")
            f.write(f"{'-'*50}\n")