#!/usr/bin/python3

# Decides which account to give to a client requesting an account.
# Stores the currently allocated accounts in a file.
# Locking blocks race conditions, since each client request forks off the
# main daemon.
# Also handles releasing account allocations by checking for signs a client
# is no longer using that Minecraft account.
