from typing import List
from rclpy.handle import InvalidHandle
from rclpy.context import Context
from rclpy.node import Node
from rclpy.timer import Timer
from rclpy.action import ActionClient, ActionServer
from rclpy.parameter import Parameter
from typing import List

class Node2(Node):

    def __init__(self, node_name: str, *, context: Context = None, cli_args: List[str] = None, namespace: str = None, use_global_arguments: bool = True, enable_rosout: bool = True, start_parameter_services: bool = True, parameter_overrides: List[Parameter] = None, allow_undeclared_parameters: bool = False, automatically_declare_parameters_from_overrides: bool = False) -> None:
        
        super().__init__(node_name, context=context, cli_args=cli_args, namespace=namespace, use_global_arguments=use_global_arguments, enable_rosout=enable_rosout, start_parameter_services=start_parameter_services, parameter_overrides=parameter_overrides, allow_undeclared_parameters=allow_undeclared_parameters, automatically_declare_parameters_from_overrides=automatically_declare_parameters_from_overrides)

        self.__action_clients: List[ActionClient] = []
        self.__action_servers: List[ActionServer] = []

    def create_action_client(self, *args, **kwargs) -> ActionClient:
        
        action_client = ActionClient(self, *args, **kwargs)

        self.__action_clients.append(action_client)

        return action_client
    
    def create_action_server(self, *args, **kwargs) -> ActionServer:

        action_server = ActionServer(self, *args, **kwargs)

        self.__action_servers.append(action_server)

        return action_server
    
    def destroy_action_client(self, action_client: ActionClient) -> bool:

        if action_client in self.__action_clients:
            self.__action_clients.remove(action_client)
            try:
                action_client.destroy()
            except InvalidHandle:
                return False
            return True
        return False
    
    def destroy_action_client_tk_safe(self, action_client: ActionClient) -> None:
        '''
        Calling ActionClient.destroy inside a callback function of tkinter leads to "Segmentation fault (core dumped)" error.
        We work around the issue by destroying the action within a one-shot timer which is executed by the nodes executor outside the tkinter callback.
        '''

        timer = self.create_timer(0.1, lambda: None)
        # assign callback after so we can pass the timer itself to the callback
        timer.callback = lambda action_client=action_client, timer=timer: self.__destroy_action_tk_safe_timer_callback(action_client, timer)

    def __destroy_action_tk_safe_timer_callback(self, action_client: ActionClient, timer: Timer) -> None:

        self.destroy_timer(timer)
        self.destroy_action_client(action_client)

    def destroy_action_server(self, action_server: ActionServer) -> bool:

        if action_server in self.__action_servers:
            self.__action_servers.remove(action_server)
            try:
                action_server.destroy()
            except InvalidHandle:
                return False
            return True
        return False
    
    def destroy_node(self) -> bool:

        while self.__action_clients:
            self.destroy_action_client(self.__action_clients[0])
        while self.__action_servers:
            self.destroy_action_server(self.__action_servers[0])

        return super().destroy_node()