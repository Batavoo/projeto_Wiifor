# import requests
# import pandas as pd
# from datetime import datetime
# import pytz

# # Current date and time in specified format
# brazil_tz = pytz.timezone('America/Sao_Paulo')
# current_time = datetime.now(brazil_tz).strftime('%Y-%m-%d %H:%M:%S')
# print(f"Current Date and Time: {current_time}")
# print(f"User: Batavoo")
# print("-" * 50)

# # Zabbix API configuration

# def zabbix_api(method, params):
#     """Function to make API calls to Zabbix"""
#     payload = {
#         "jsonrpc": "2.0",
#         "method": method,
#         "params": params,
#         "auth": token,
#         "id": 1
#     }
    
#     try:
#         response = requests.post(url, json=payload, headers=headers)
#         response_data = response.json()
        
#         if 'result' in response_data:
#             return response_data["result"]
#         else:
#             print(f"API Error: {response_data.get('error', 'Unknown error')}")
#             return []
#     except Exception as e:
#         print(f"Connection Error: {str(e)}")
#         return []

# # Get some sample hosts
# print("Fetching sample hosts...")
# hosts = zabbix_api("host.get", {
#     "output": ["hostid", "host", "name"],
#     "limit": 5  # Just get a few hosts for testing
# })

# if not hosts:
#     print("No hosts found. Exiting.")
#     exit()

# print(f"Found {len(hosts)} hosts for testing.")

# # List of potential CPU and memory related keywords to search for
# cpu_keywords = ["cpu", "processor", "proc", "system.cpu", "perf_counter", "utilizat"]
# memory_keywords = ["memory", "mem", "ram", "swap", "system.mem", "vm.memory"]

# # Compile all keyword searches
# all_keywords = cpu_keywords + memory_keywords

# # For each host, search for items with these keywords
# print("\nSearching for CPU and memory metrics across hosts...")
# print("-" * 50)

# all_metrics = []

# for host in hosts:
#     print(f"\nChecking host: {host['name']} ({host['host']})")
    
#     # Search for items matching our keywords
#     for keyword in all_keywords:
#         items = zabbix_api("item.get", {
#             "output": ["itemid", "name", "key_", "lastvalue", "units", "valuetype"],
#             "hostids": host["hostid"],
#             "search": {"key_": keyword},
#             "searchWildcardsEnabled": True
#         })
        
#         if items:
#             print(f"  Found {len(items)} items matching '{keyword}'")
#             for item in items:
#                 # Add host info to each item
#                 item["host_name"] = host["name"]
#                 item["host_id"] = host["hostid"]
#                 all_metrics.append(item)

# # Process results
# if all_metrics:
#     # Convert to DataFrame for easier analysis
#     df = pd.DataFrame(all_metrics)
    
#     # Remove duplicates based on key_
#     df = df.drop_duplicates(subset=['key_'])
    
#     # Categorize as CPU or Memory
#     def categorize_metric(key):
#         key_lower = key.lower()
#         if any(cpu_key in key_lower for cpu_key in cpu_keywords):
#             return "CPU"
#         elif any(mem_key in key_lower for mem_key in memory_keywords):
#             return "Memory"
#         else:
#             return "Other"
    
#     df['category'] = df['key_'].apply(categorize_metric)
    
#     # Print summary of potential metrics
#     print("\nPotential CPU and Memory Metrics Found:")
#     print("-" * 50)
    
#     # Print CPU metrics
#     print("\nCPU Metrics:")
#     print("-" * 50)
#     cpu_metrics = df[df['category'] == 'CPU']
#     for _, row in cpu_metrics.iterrows():
#         print(f"Name: {row['name']}")
#         print(f"Key: {row['key_']}")
#         print(f"Last Value: {row['lastvalue']} {row['units']}")
#         print(f"Found in host: {row['host_name']}")
#         print("-" * 30)
    
#     # Print Memory metrics
#     print("\nMemory Metrics:")
#     print("-" * 50)
#     mem_metrics = df[df['category'] == 'Memory']
#     for _, row in mem_metrics.iterrows():
#         print(f"Name: {row['name']}")
#         print(f"Key: {row['key_']}")
#         print(f"Last Value: {row['lastvalue']} {row['units']}")
#         print(f"Found in host: {row['host_name']}")
#         print("-" * 30)
    
#     # Recommendation
#     print("\nRecommended Metrics for Dashboard:")
#     print("-" * 50)
    
#     # Try to find the best CPU metric
#     best_cpu = None
#     for cpu_key in ["system.cpu.util", "system.cpu.load", "proc.cpu.util"]:
#         matches = cpu_metrics[cpu_metrics['key_'].str.contains(cpu_key, case=False)]
#         if not matches.empty:
#             best_cpu = matches.iloc[0]
#             break
    
#     if best_cpu is not None:
#         print(f"CPU Recommendation: {best_cpu['name']} (key: {best_cpu['key_']})")
#     else:
#         print("No ideal CPU metric found. Review the list above.")
    
#     # Try to find the best Memory metric
#     best_mem = None
#     for mem_key in ["system.mem.util", "vm.memory.utilization", "vm.memory.size"]:
#         matches = mem_metrics[mem_metrics['key_'].str.contains(mem_key, case=False)]
#         if not matches.empty:
#             best_mem = matches.iloc[0]
#             break
    
#     if best_mem is not None:
#         print(f"Memory Recommendation: {best_mem['name']} (key: {best_mem['key_']})")
#     else:
#         print("No ideal Memory metric found. Review the list above.")
# else:
#     print("No CPU or Memory metrics found for the sampled hosts.")
#     print("You may need to check if these metrics are configured in your Zabbix setup.")