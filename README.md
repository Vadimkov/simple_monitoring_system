# simple_monitoring_system
Simple system for monitoring files on the different hosts

It is my pet project for learning Python.

This system has following architecture:
1. One monitoring_center.py - one service for system for collect and handle all data.
2. monitoring_agent.py - one agent for every host or network. Agent should monitore selected files/directories and push all changes to the center.
3. monitoring_client.py - client able to connect to the center, send filter, and center will send in response all files (host, directory, type and file), matched by this filter.
4. some handlers - center able to run some handler of data. For example: send email, push updates to wiki page and etc...

The system resolve my problem of controle credentials in the big company with a lot of hosts and networks.
In the future user will able to write custom scripts (I'll be use nice work "extension") for monitoring data in the agent and handler for center.
