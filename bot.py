from time import sleep
import time
import logging
from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler
from user import User
from usertoken import Token
import config as cfg

class SurveillanceBot():
    
    def __init__(self):
        ''' Inits and starts bot '''
        
        #: Setup updater and dispatcher
        self.updater = Updater(token=cfg.TELEGRAM_API_TOKEN)
        self.dispatcher = self.updater.dispatcher
        
        #: Logging setup
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', level=logging.DEBUG)
        
        #: Register activate-command-handler
        open_activate_command_handler = CommandHandler('activate', self.open_activate_command_callback)
        self.dispatcher.add_handler(open_activate_command_handler)
        
        #: Register user-command-handler
        mod_show_users_with_roles_command_handler = CommandHandler('users', self.mod_show_users_with_roles_command_callback)
        self.dispatcher.add_handler(mod_show_users_with_roles_command_handler)
        
        #: Register token-command-handler
        admin_create_token_command_handler = CommandHandler('token', self.admin_create_token_command_callback)
        self.dispatcher.add_handler(admin_create_token_command_handler)
        
        #: Register clear-command-handler
        owner_clear_all_users_and_admins_command_handler = CommandHandler('clear', self.owner_clear_all_users_and_admins_command_callback)
        self.displatcher.add_handler(owner_clear_all_users_and_admins_command_handler)
        
        #: Init users and admin dict
        self.users = {}
        self.admins = {}
        self.banned = {}
        
        self.tokens = {}
        
        #: Register owner token
        owner_token = Token(cfg.OWNER_ROLE, 1)
        owner_token.value = cfg.OWNER_ACTIVATION_TOKEN
        self.tokens[owner_token.value] = owner_token
        
        #: Set whether or not users can request tokens
        self.is_request_tokens_enabled = cfg.REQUEST_TOKENS_ENABLED
        
        #: Start
        self.updater.start_polling()
        

    def open_activate_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /activate command - OPEN
            
            Checks if the entered token is valid.
            Informs the user to be activated when successful.
        '''
        
        chat_id = update.effective_chat.id
        
        ### Check authorization ###
        authorization_level = cfg.ROLE_RANKING[cfg.OPEN_ROLE]
        if not self._is_authorized(chat_id, authorization_level):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        ###########################
        
        #: Remove expired tokens
        self._clean_tokens()
        
        #: check if provided token is valid
        if context.args and context.args[0] in self.tokens:
            
            #: remove token
            token = self.tokens.pop(context.args[0])
            
            #: create and save user
            user = User(chat_id, update.message.from_user.username, token.role)
            self.users[chat_id] = user
            
            #: add as admin if token allows
            if cfg.ROLE_RANKING[token.role] >= cfg.ROLE_RANKING[cfg.ADMIN_ROLE]:
                self.admins[chat_id] = user
            
            #: inform user
            self._send_text_msg(chat_id, text='Subscribed!')         

    def mod_show_users_with_roles_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /users command - ADMIN

            Shows current users to the admin
        '''
        
        chat_id = update.effective_chat.id
        
        ### Check authorization ###
        authorization_level = cfg.ROLE_RANKING[cfg.MOD_ROLE]
        if not self._is_authorized(chat_id, authorization_level):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        ###########################
        
        if update.effective_chat.id in self.admins:
            context.bot.send_message(chat_id=update.effective_chat.id, text='List of users ...')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Unauthorized!')
            
    def admin_create_token_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /token command - ADMIN

            Allows admins to create register-tokens.
            
            #: -a admin-token
            #: -m mod-token
            #: -u user-token (default)
        '''
        chat_id = update.effective_chat.id
        
        ### Check authorization ###
        authorization_level = cfg.ROLE_RANKING[cfg.ADMIN_ROLE]
        if not self._is_authorized(chat_id, authorization_level):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        ###########################
        
        if not context.args or context.args[0] not in cfg.TOKEN_OPTIONS:
            self._send_text_msg(chat_id, 'Please use one of the options: -a for admin, -m for mod, -s for subscriber.')
            return
        
        role = cfg.TOKEN_OPTIONS[context.args[0]]
        
        if not cfg.ROLE_RANKING[self.users[chat_id].role] > cfg.ROLE_RANKING[role]:
            self._send_text_msg(chat_id, 'You can only generate tokens for roles lower than your own.')
            return
        
        if len(context.args) > 1 and not context.args[1].isnumeric():
            self._send_text_msg(chat_id, 'If you want to provide a period of validity, please use numeric values only. Default is 1 day.')
            return
        
        role = cfg.TOKEN_OPTIONS[context.args[0]]
        token = Token(role, context.args[1] if len(context.args) > 1 else 1)
        self.tokens[token.value] = token
        
        self._send_text_msg(chat_id, 'Newly created {role} token: {token}'.format(role = role, token = token.value))
    
    def owner_clear_all_users_and_admins_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /clear command - OWNER

            Clears all users and admins except the owner
        '''
        chat_id = update.effective_chat.id
        
        ### Check authorization ###
        authorization_level = cfg.ROLE_RANKING[cfg.OWNER_ROLE]
        if not self._is_authorized(chat_id, authorization_level):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        ###########################
        
        owner = self.users.pop(chat_id)
        
        self._send_text_msg_to_lst(self.users, 'Your subscription was terminated.')
        
        self.admins.clear()
        self.users.clear()
        self.admins[chat_id] = owner
        self.users[chat_id] = owner
    
    def alert(self) -> None:
        ''' Method to inform all subscribers when motion was detected.
            Is called by the MotionDetectionHandler.
        '''
        
        self._send_text_msg_to_lst(self.users, 'Movement detected!')
        
    def send_surveillance_video(self, video) -> None:
        ''' Sends the recorded surveillance video to every admin-user
        '''
        
        if not video:
            return
        
        #: Iterate admins and send video to each
        for admin in self.admins: 
            self.updater.bot.send_video(admin, open(video, 'rb'), True)
    
    def _is_authorized(self, chat_id, command_authorization_level) -> bool:
        ''' Check if user with given chat_id is authorized for command

            #: chat_id                     - telegram chat_id
            #: command_authorization_level - required authorization level to execute command
        '''
        
        #: Banned chat_ids are never authorized
        if chat_id in self.banned:
            return False
        
        #: Command authorization level must be open, or the user has to be registered and own the required access rights
        return command_authorization_level == cfg.ROLE_RANKING[cfg.OPEN_ROLE] or (chat_id in self.users and cfg.ROLE_RANKING[self.users[chat_id].role] >= command_authorization_level)
    
    def _clean_tokens(self) -> None:
        ''' Cleans token dict from expired tokens
        '''
        
        #: Remove expired tokens in dict comprehension filter
        self.tokens = { k:v for k,v in self.tokens.items() if v.is_valid() }
    
    def _send_text_msg_to_lst(self, lst, text) -> None:
        ''' Sends message to list of chat_ids

            #: lst  - list of chat_ids
            #: text - message text
        '''
        
        #: Iterate over given list and send message to each user
        for user in lst: 
            self.updater.bot.send_message(chat_id=chat_id, text=text)
    
    def _send_text_msg(self, chat_id, text) -> None:
        ''' Sends message to chat_id

            #: chat_id  - telegram chat_id
            #: text     - message text
        '''
        self.updater.bot.send_message(chat_id=chat_id, text=text)
        
    