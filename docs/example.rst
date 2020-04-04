.. _example:

Full Example
============

The power of this library is it's declarative interface. Here we can quickly build a menu 
around an example network program.

.. code-block:: python

    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import NestedCompleter

    from prompt_smart_menu import PromptSmartMenu
    from prompt_smart_menu.helpers import InvalidArgError

    from example.network import connections, devices

    connection_list = connections.list()
    device_list = devices.list()

    def help():
        print("Use tab completion to input your command.")

    menu_config = [
        {
            'command': 'connection',
            'children': [
                {
                    'command': 'list',
                    'function': lambda: print(connection_list),
                },
                {
                    'command': 'show',
                    'function': connections.show,
                    'children': connection_list,
                },
                {
                    'command': 'up',
                    'function': connections.up,
                    'children': connection_list,
                },
                {
                    'command': 'down',
                    'function': connections.down,
                    'children': connection_list,
                }

            ]
        },
        {
            'command': 'device',
            'children': [
                {
                    'command': 'list',
                    'function': lambda: print(device_list),
                },
                {
                    'command': 'show',
                    'function': devices.show,
                    'children': device_list,
                },
                {
                    'command': 'connect',
                    'function': devices.connect,
                    'children': device_list,
                },
                {
                    'command': 'disconnect',
                    'function': devices.disconnect,
                    'children': device_list,
                }

            ]
        },
        {
            'command': 'help',
            'function': help,
        },
        {
            'command': 'exit',
            'function': exit,
        }
    ]


    def main():
        psm = PromptSmartMenu(menu_config, validate_args=True)
        completer_dict = psm.nested_completer_dict()

        completer = NestedCompleter.from_nested_dict(completer_dict)

        session = PromptSession(completer=completer)
        while True:
            try:
                command = session.prompt('network ')
                try:
                    psm.run(command)
                except InvalidArgError as err:
                    print(f'Bad input: {err}')
            except KeyboardInterrupt:
                continue
            except EOFError:
                break

    if __name__ == '__main__':
        main()
