import os 
import json 
import asyncio

import threading
import discord

VERBOSE = True

# PATHS VARIABLES

PATH_FOLDER_CONFIG = os.path.join("~/.discord_bot_chatter/")
PATH_FOLDER_CONFIG_ABS = os.path.expanduser(PATH_FOLDER_CONFIG) 
PATH_FILE_CONFIG_DEFAULT = os.path.join(PATH_FOLDER_CONFIG_ABS,"config.json")

def print_msg(msg): 
    if(VERBOSE): 
        print(msg)

def print_error(msg):
    print(f"[ERROR] {msg}")

def start_async(function): 
    """start async fuction 

    Args:
        function (def): async function to start

    Returns:
        loop (EventLoop): loop managing async methods
    """
    asyncio.get_child_watcher()
    loop = asyncio.get_event_loop()
    loop.create_task(function)
    return loop 

class HandlerJobs: 

    def __init__(self,callback): 
        self._jobs_registered = []
        self._jobs_ended = []
        self._jobs_pool = []
        self._callback = callback

    def add_job_to_pool(self,job):
        self._jobs_pool.append(job)
    
    def execute_pool(self):
        """execute all jobs available in the jobs_pool
        """
        for job in self._jobs_pool:
            print_msg(f"job from the pool started: {job}")
            job.do()
        self._jobs_pool = []

    def register(self,job): 
        """get the job declaration and attach a callback to the job
        This callback allows to trig an event when the job is ended. 
        Args:
            job (Job): job to register
        """
        self._jobs_registered.append(job)
        job.attach_callback(lambda : self.end(job))

    def end(self,job): 
        """function called at end of each job, and trig the callback handler 

        Args:
            job (Job): job ended 
        """
        self._jobs_ended.append(job)
        self._callback(job) 

    def jobs_running(self): 
        """get all jobs currently running

        Returns:
            set: set difference between registered jobs and ended jobs 
        """
        return set(self._jobs_registered) - set(self._jobs_ended)

    def count_jobs_running(self):
        return len(list((self.jobs_running())))

class Job: 

    COUNTER = 0

    def __init__(self,function,*args): 
        self._function = function
        self._args = args
        self._callback_end = None
        self._id = Job.COUNTER
        Job.COUNTER += 1

    def attach_callback(self,callback): 
        self._callback_end = callback

    def do(self,_async=True):
        if(_async): 
            callback = self._callback_end
            start_async(self._function(callback,*self._args))
        else: 
            self.function(*self._args)

    def __repr__(self): 
        return f"func: {self._function.__name__} args: {self._args}"

class Message: 

    def __init__(self,content): 
        self.content = content

    def to_block_code(self): 
        return f"> {self.content}"

    def to_block_quote(self):
        return f"```{self.content}```"

    def __repr__(self):
        return self.content

class ConnectionStatus: 
    CONNECT = 1
    TRY_CONNECT = 2
    DISCONNECT = 11
    TRY_DISCONNECT = 12

class BotChatter: 

    def LOAD_CONFIG(path_file):
        """load configuration from path_file

        Args:
            path_file (string): path to the json config file

        Returns:
            dict: information loaded from json
        """
        data = None
        try:
            with open(path_file) as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            print_error(f"file {path_file} not find")
            exit(-1)
        except ValueError:
            print_error(f"can't decode {path_file} file")
            exit(-1)
        finally:
            return data

    def __init__(self,bot_name,server_name,
                 default_channel_name=None,
                 path_config=None): 

        # client variables
        self._bot_name = bot_name
        self._server_name = server_name
        self._connection_status = ConnectionStatus.DISCONNECT  
        self._handler_jobs = HandlerJobs(self._disconnect_safe)

        if(path_config == None):
            path_config = PATH_FILE_CONFIG_DEFAULT
        self._config = BotChatter.LOAD_CONFIG(path_config)

        self._token = self._extract_token(bot_name)
        self._server_id = self._extract_server_id(server_name)

        # extract channel id 
        if(default_channel_name != None): 
            self._default_channel_id = self._extract_channel_id(server_name,default_channel_name)

    def _try_to_do(self,job):
        """if the client isn't connected, the job is added to the pool
           else the job is done directly 

        Args:
            job (Job): job to realize
        """
        if(self._connection_status == ConnectionStatus.CONNECT): 
            job.do()
        else: 
            print_msg(f"job added to the pool: {job}")
            self._handler_jobs.add_job_to_pool(job)

    # extract config information functions

    def _extract_server_id(self,server_name): 
        return int(self._config["servers"][server_name]["id"])

    def _extract_channel_id(self,server_name,channel_name): 
        return int(self._config["servers"][server_name]["channels"][channel_name])

    def _extract_token(self,bot_name): 
        return self._config["bots"][bot_name]["token"]

    # connection functions 

    async def _async_connection_start(self):
        await self._client.start(self._token)

    def _connection_loop(self,loop):
        loop.run_forever()

    # event functions 

    async def on_ready(self):
        for guild in self._client.guilds:
            if guild.id == self._server_id:
                self._connection_status = ConnectionStatus.CONNECT
                break
        
        if(self._connection_status == ConnectionStatus.CONNECT): 
            self._handler_jobs.execute_pool()

    # async functions

    async def _async_disconnect(self,callback): 
        self._connection_status = ConnectionStatus.TRY_DISCONNECT  
        callback()

    def _disconnect_safe(self,job):
        """check if the connection can't be close or not 

        Args:
            job (Job): job ended
        """
        print_msg(f"job ended: {job}")
        if(self._connection_status == ConnectionStatus.TRY_DISCONNECT  and 
            self._handler_jobs.count_jobs_running() == 0): 
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._connection_status = ConnectionStatus.DISCONNECT
        
    async def _async_send_message(self,callback,message,channel_id):
        channel = self._client.get_channel(channel_id)
        await channel.send(message) 
        callback()

    async def _async_send_img(self,callback,path_file,channel_id):
        channel = self._client.get_channel(channel_id)
        await channel.send(file=discord.File(path_file))
        callback()

    # user functions

    def connect(self): 
        self._connection_status = ConnectionStatus.TRY_CONNECT 
        self._client = discord.Client() 
        self._client.event(self.on_ready)
        self._loop = start_async(self._async_connection_start())
        self._thread = threading.Thread(target=self._connection_loop, args=(self._loop,))
        self._thread.start()

    def disconnect(self): 
        job = Job(self._async_disconnect)
        self._handler_jobs.register(job)
        self._try_to_do(job)

    def send_message(self,message,channel_name=None):
        channel_id = self._default_channel_id
        if(channel_name != None):
            channel_id = self._extract_channel_id(self._server_name,channel_name)
        job = Job(self._async_send_message,message,channel_id)
        self._handler_jobs.register(job)
        self._try_to_do(job)

    def send_img(self,path_file,channel_name=None):
        channel_id = self._default_channel_id
        if(channel_name != None):
            channel_id = self._extract_channel_id(self._server_name,channel_name)
        job = Job(self._async_send_img,path_file,channel_id)
        self._handler_jobs.register(job)
        self._try_to_do(job)


    # builtin functions 

    def __repr__(self): 
        content = ""
        content += f"bot_name: {self._bot_name} \n"
        content += f"server_id: {self._id_server}\n"
        content += f"token_id: {self._id_token}"
        return content 
