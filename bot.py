import string
import logging
from time import strftime
from typing import Callable
from telegram import Message, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, CallbackQueryHandler
from payload import Payload

import utils
import config as cfg
#from userservice import UserService
from user import User
from usertoken import Token

class SurveillanceBot:
    
    def __init__(self, pause_unpause_callback: Callable):
        ''' Inits and starts bot '''
        
        #: Setup updater and dispatcher
        self.updater = Updater(token=cfg.TELEGRAM_API_TOKEN)
        self.dispatcher = self.updater.dispatcher
        
        #: Init logger
        self.logger = logging.getLogger(__name__)
        
        #: Save callback
        self.pause_unpause_callback = pause_unpause_callback
        
        #: Register activate-command-handler
        open_activate_command_handler = CommandHandler('activate', self.open_activate_command_callback)
        self.dispatcher.add_handler(open_activate_command_handler)
        
        #: Register leave-command-handler
        open_leave_command_handler = CommandHandler('leave', self.open_leave_command_callback)
        self.dispatcher.add_handler(open_leave_command_handler)
        
        #: Register user-command-handler
        mod_show_users_with_roles_command_handler = CommandHandler('users', self.mod_show_users_with_roles_command_callback)
        self.dispatcher.add_handler(mod_show_users_with_roles_command_handler)
        
        #: Register token-command-handler
        admin_create_token_command_handler = CommandHandler('token', self.admin_create_token_command_callback)
        self.dispatcher.add_handler(admin_create_token_command_handler)

        #: Register cleartokens-command-handler
        admin_clear_tokens_command_handler = CommandHandler('cleartokens', self.admin_clear_tokens_command_callback)
        self.dispatcher.add_handler(admin_clear_tokens_command_handler)
        
        #: Register pause-command-handler
        admin_pause_command_handler = CommandHandler('pause', self.admin_pause_command_callback)
        self.dispatcher.add_handler(admin_pause_command_handler)
        
        #: Register unpause-command-handler
        admin_unpause_command_handler = CommandHandler('unpause', self.admin_unpause_command_callback)
        self.dispatcher.add_handler(admin_unpause_command_handler)

        #: Register ban-command-handler
        admin_ban_user_command_handler = CommandHandler('ban', self.admin_ban_user_command_callback)
        self.dispatcher.add_handler(admin_ban_user_command_handler)

        #: Register unban-command-handler
        admin_unban_user_command_handler = CommandHandler('unban', self.admin_unban_user_command_callback)
        self.dispatcher.add_handler(admin_unban_user_command_handler)
        
        #: Register clear-command-handler
        owner_clear_all_command_handler = CommandHandler('clear', self.owner_clear_all_command_callback)
        self.dispatcher.add_handler(owner_clear_all_command_handler)

        self.dispatcher.add_handler(CallbackQueryHandler(self.button))
        
        #: Init users and admin dict
        self.users = {}
        self.banned = {}
        
        #TODO remove test users
        for i in range(4):
            user = User(utils.randomstr(10, string.digits), utils.randomstr(8, string.ascii_lowercase), 1)
            self.users[user.chat_id] = user
        
        self.tokens = {}
        
        #: Register owner token
        owner_token = Token(cfg.ROLE_TO_RANK[cfg.OWNER_ROLE], 1)
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
        authorization_level = cfg.ROLE_TO_RANK[cfg.OPEN_ROLE]
        if not self._is_authorized(chat_id, authorization_level):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        
        #: Remove expired tokens
        self._clean_tokens()
        
        #: catch invalid token
        if not context.args or context.args[0] not in self.tokens:
            
            #: inform user
            self._send_text_msg(chat_id, text='Token invalid.')
            return
            
        #: get and remove token
        token = self.tokens.pop(context.args[0])
        
        #: create and save user
        user = User(chat_id, update.message.from_user.username, token.role)
        self.users[chat_id] = user
        
        #: inform user
        self._send_text_msg(chat_id, text='Registered succesfully as {}!'.format(cfg.ROLES[cfg.RANK_TO_ROLE[token.role]]))
        
    def open_leave_command_callback(self, update: Update, context: CallbackContext) -> None:
        
        chat_id = update.effective_chat.id
        
        ### Check authorization ###
        authorization_level = cfg.ROLE_TO_RANK[cfg.OPEN_ROLE]
        if not self._is_authorized(chat_id, authorization_level):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        
        if self.users[chat_id].role == cfg.ROLE_TO_RANK[cfg.OWNER_ROLE]:
            
            #: inform user: owner cant leave
            self._send_text_msg(chat_id, text='You cant leave as the owner.')
            return
        
        if chat_id not in self.users:
            
            #: inform user: cannot leave if not registered
            self._send_text_msg(chat_id, text='You are not registered.')
        
        else:
            
            #: remove user
            del self.users[chat_id]
            
            #: inform user: left successfully
            self._send_text_msg(chat_id, text='You are no longer registered.')
            

    def mod_show_users_with_roles_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /users command - ADMIN

            Shows current users to the admin
        '''
        
        chat_id = update.effective_chat.id
        
        ### Check authorization ###
        authorization_level = cfg.ROLE_TO_RANK[cfg.MOD_ROLE]
        if not self._is_authorized(chat_id, authorization_level):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        
        context.bot.send_message(chat_id=update.effective_chat.id, text=self._get_all_users_as_text())
            
    def admin_create_token_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /token command - ADMIN
            Allows admins to create register-token
            
            #: handles a multi stage query for token creation
        '''

        chat_id = update.effective_chat.id
        query = update.callback_query
        
        ### Check authorization ###
        authorization_level = cfg.ROLE_TO_RANK[cfg.ADMIN_ROLE]
        if not self._is_authorized(chat_id, authorization_level):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return

        #: Start process
        if not query:

            #: build role option keyboard
            keyboard = [[InlineKeyboardButton(cfg.ROLES[cfg.RANK_TO_ROLE[i]], callback_data=i),] for i in range(1, 4)]
            reply_markup = InlineKeyboardMarkup(keyboard)

            #: Send query for role options
            message = update.message.reply_text("Choose the authority level for the token:", reply_markup=reply_markup)

            #: save payload
            self._add_query_payload(message, context, self.admin_create_token_command_callback, None, 1)

        #: If query exists, handle user selection based on stage
        else:
            
            #: get payload regarding message
            payload: Payload = context.bot_data[query.message.message_id]

            #: handle first user selection
            if payload.stage == 1:
                
                #: build days of validity option keyboard
                keyboard = [
                    [InlineKeyboardButton(1, callback_data=1), InlineKeyboardButton(3, callback_data=3)],
                    [InlineKeyboardButton(5, callback_data=5), InlineKeyboardButton(10, callback_data=10)]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                #: update stage and save user seletion for later in payload data
                payload.stage = 2
                payload.data = query.data

                #: update query with days of validity options
                query.edit_message_text(text="Choose days of validity:")
                query.edit_message_reply_markup(reply_markup=reply_markup)
                
                return

            #: handle second user selection
            if payload.stage == 2:
                
                #: build token based on seletions
                t = Token(int(payload.data), int(query.data))

                self.logger.debug('New {} token created'.format(cfg.RANK_TO_ROLE[t.role]))
                
                #: inform user with new token
                query.edit_message_text('{} token is valid until {}'.format(cfg.ROLES[cfg.RANK_TO_ROLE[t.role]].capitalize(), t.valid_until.strftime('%y/%m/%d, %H:%M')))
                update.message.reply_text(t.value)
                
                #: remove payload from context
                del context.bot_data[query.message.message_id]
                
                return 


    def admin_clear_tokens_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /clear command - ADMIN
        '''

        chat_id = update.effective_chat.id
        
        ### Check authorization ###
        authorization_level = cfg.ROLE_TO_RANK[cfg.ADMIN_ROLE]
        if not self._is_authorized(chat_id, authorization_level):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return

        self.tokens.clear()
        
    def admin_pause_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /pause command - ADMIN
        '''

        chat_id = update.effective_chat.id
        
        ### Check authorization ###
        authorization_level = cfg.ROLE_TO_RANK[cfg.ADMIN_ROLE]
        if not self._is_authorized(chat_id, authorization_level):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return

        if self.pause_unpause_callback(True):
            self._send_text_msg(chat_id, 'Surveillance deactivated.')
            
        else:
            self._send_text_msg(chat_id, 'Surveillance already inactive.')
        
    def admin_unpause_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /unpause command - ADMIN
        '''

        chat_id = update.effective_chat.id
        
        ### Check authorization ###
        authorization_level = cfg.ROLE_TO_RANK[cfg.ADMIN_ROLE]
        if not self._is_authorized(chat_id, authorization_level):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return

        if self.pause_unpause_callback(False):
            self._send_text_msg(chat_id, 'Surveillance activated.')
            
        else:
            self._send_text_msg(chat_id, 'Surveillance already active.')
        

    def admin_ban_user_command_callback(self, update: Update, context: CallbackContext) -> None:
        '''
        '''

        chat_id = update.effective_chat.id
        
        ### Check authorization ###
        authorization_level = cfg.ROLE_TO_RANK[cfg.ADMIN_ROLE]
        if not self._is_authorized(chat_id, authorization_level):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        
        if not [i for i in self.users.keys() if i != chat_id]:
            self._send_text_msg(chat_id, 'There is no user you could ban.')
            return
        
        self._admin_ban_unban_user_helper(update, context, self.admin_ban_user_command_callback, self.users, self.banned, 'banned')
        

    def admin_unban_user_command_callback(self, update: Update, context: CallbackContext) -> None:
        '''
        '''

        chat_id = update.effective_chat.id
        
        ### Check authorization ###
        authorization_level = cfg.ROLE_TO_RANK[cfg.ADMIN_ROLE]
        if not self._is_authorized(chat_id, authorization_level):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return

        self._admin_ban_unban_user_helper(update, context, self.admin_unban_user_command_callback, self.banned, self.users, 'unbanned')

    def _admin_ban_unban_user_helper(self, update: Update, context: CallbackContext, callback: Callable, from_dict: dict, to_dict: dict, action_name: str):
        
        chat_id = update.effective_chat.id
        query = update.callback_query
        
        #: Start process
        if not query:
            
            #: get role of current user
            role = self.users[chat_id].role
        
            #: build ban-unban-user option keyboard
            keyboard = [[InlineKeyboardButton(user.name, callback_data=user.chat_id)] for user in from_dict.values() if user.role < role]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            #: send query
            message = update.message.reply_text("Select the user to be {}:".format(action_name), reply_markup=reply_markup)
            
            self._add_query_payload(message, context, callback)
            
        #: If query exists, handle user selection
        else:
            
            self.logger.warn("User to be moved")
            
            if query.data not in from_dict:
                return #TODO user not found
            
            user_to_move = from_dict.pop(query.data)
            to_dict[user_to_move.chat_id] = user_to_move
            
            self.logger.warn("User moved")
            
            #: inform user with new token
            query.edit_message_text('{} was {}.'.format(user_to_move.name, action_name))
            
            #: remove payload from context
            del context.bot_data[query.message.message_id]
        
        
    def owner_clear_all_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /clear command - OWNER

            Clears all users and admins except the owner
        '''

        chat_id = update.effective_chat.id
        
        ### Check authorization ###
        authorization_level = cfg.ROLE_TO_RANK[cfg.OWNER_ROLE]
        if not self._is_authorized(chat_id, authorization_level):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        
        #
        owner = self.users.pop(chat_id)
        
        self._send_text_msg_to_lst(self.users, 'Your subscription was terminated.')

        self.tokens.clear()
        
        self.users.clear()
        self.users[chat_id] = owner


    def button(self, update: Update, context: CallbackContext) -> None:
        """Parses the CallbackQuery and updates the message text."""
        
        query = update.callback_query
        message_id = query.message.message_id


        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
        query.answer()

        #: abort if no handler is filed
        if message_id not in context.bot_data:
            #TODO handle error
            return

        #: delegate query data to filed handler method
        context.bot_data[message_id].callback(update, context)

    
    def alert(self, msg: str, role_level = 0) -> None:
        ''' Method to inform specified user group with custom message
        '''
        
        self._send_text_msg_to_lst({k: v for k, v in self.users.items() if v.role >= role_level }, msg)
        
    def send_surveillance_video(self, video_path: str) -> None:
        ''' Sends the recorded surveillance video to every admin-user
        '''
        
        if not video_path:
            return
        
        #: Iterate admins and send video to each
        for admin in self.users: 
            self.updater.bot.send_video(chat_id=admin, video=open(video_path, 'rb'), supports_streaming=True,  caption=utils.basename(video_path))
    
    def _add_query_payload(self, message: Message, context: CallbackContext, callback: Callable, data: object = None, stage: int = None):

        payload_dict = { message.message_id: Payload(data, stage, callback) }

        context.bot_data.update(payload_dict)

    def _is_authorized(self, chat_id, command_authorization_level) -> bool:
        ''' Check if user with given chat_id is authorized for command

            #: chat_id                     - telegram chat_id
            #: command_authorization_level - required authorization level to execute command
        '''
        
        #: Banned chat_ids are never authorized
        if chat_id in self.banned:
            return False
        
        #: Command authorization level must be open, or the user has to be registered and own the required access rights
        return command_authorization_level == cfg.ROLE_TO_RANK[cfg.OPEN_ROLE] or (chat_id in self.users and self.users[chat_id].role >= command_authorization_level)
    
    def _clean_tokens(self) -> None:
        ''' Cleans token dict from expired tokens
        '''
        
        #: Remove expired tokens in dict comprehension filter
        self.tokens = { k:v for k,v in self.tokens.items() if v.is_valid() }

    def _ban(self, chat_id) -> None:
        ''' Bans user
        '''
        
        print(" USER BANNED !!!!")

    def _unban(self, chat_id) -> None:
        ''' Cleans token dict from expired tokens
        '''
        
        print(" USER UNBANNED !!!!")
    
    def _send_text_msg_to_lst(self, lst, text) -> None:
        ''' Sends message to list of chat_ids

            #: lst  - list of chat_ids
            #: text - message text
        '''
        
        #: Iterate over given list and send message to each user
        for user in lst: 
            self.updater.bot.send_message(chat_id=user, text=text)
    
    def _send_text_msg(self, chat_id, text) -> None:
        ''' Sends message to chat_id

            #: chat_id  - telegram chat_id
            #: text     - message text
        '''
        self.updater.bot.send_message(chat_id=chat_id, text=text)

    def _get_all_users_as_text(self) -> str:

        lst = ['{:14s} [ {:6s} ]'.format(u.name, cfg.ROLES[cfg.RANK_TO_ROLE[u.role]]) for u in self.users.values()]
        return '\n'.join(lst)
        
    
