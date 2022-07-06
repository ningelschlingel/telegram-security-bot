import string
import logging
from time import strftime
from typing import Callable, Dict
from telegram import CallbackQuery, Message, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, CallbackQueryHandler
from payload import Payload
from role import Role
from userservice import UserDict, UserService

import utils
import config as cfg
#from userservice import UserService
from user import User
from usertoken import Token

class SurveillanceBot:
    
    def __init__(self, pause_unpause_callback: Callable):
        ''' Inits and starts bot '''
        
        #: Init logger
        self.logger = logging.getLogger(__name__)

        #: Setup updater and dispatcher
        self.updater = Updater(token=cfg.TELEGRAM_API_TOKEN)
        self.dispatcher = self.updater.dispatcher

        #: Setup user service, UserService.__init__ already creates owner token
        self.userservice: UserService = UserService()
        
        #: Save callback
        self.pause_unpause_callback = pause_unpause_callback
        
        #: Register activate-command-handler
        open_activate_command_handler = CommandHandler('activate', self.open_activate_command_callback)
        self.dispatcher.add_handler(open_activate_command_handler)
        
        #: Register leave-command-handler
        open_leave_command_handler = CommandHandler('leave', self.open_leave_command_callback)
        self.dispatcher.add_handler(open_leave_command_handler)
        
        #: Register users-command-handler
        mod_show_users_with_roles_command_handler = CommandHandler('users', self.mod_show_users_with_roles_command_callback)
        self.dispatcher.add_handler(mod_show_users_with_roles_command_handler)

        #: Register banned-command-handler
        mod_show_banned_with_roles_command_handler = CommandHandler('banned', self.mod_show_banned_with_roles_command_callback)
        self.dispatcher.add_handler(mod_show_banned_with_roles_command_handler)
        
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

        #: Register handler for query callbacks
        self.dispatcher.add_handler(CallbackQueryHandler(self.button))
        
        #: Start
        self.updater.start_polling()
        

    def open_activate_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /activate command - OPEN
            
            Checks if the entered token is valid.
            Informs the user to be activated when successful.
        '''
        
        chat_id: int = update.effective_chat.id
        
        ### Check authorization ###
        req_role: Role = Role.OPEN
        if not self._is_authorized(chat_id, req_role):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        
        #: catch missing arg error
        if not context.args:
            
            #: inform user
            self._send_text_msg(chat_id, text='No token provided.')
            return
        
        #: activate token
        user: User = self.userservice.activate_token(context.args[0], chat_id, update.message.from_user.username)

        #: user exists if activation was successful
        if user:
            self._send_text_msg(chat_id, text='Registered succesfully as {}!'.format(user.role.name.lower()))

        #: otherwise token was invalid
        else:
            self._send_text_msg(chat_id, text='Invalid token.')

        
    def open_leave_command_callback(self, update: Update, context: CallbackContext) -> None:
        
        chat_id: int = update.effective_chat.id
        
        ### Check authorization ###
        req_role: Role = Role.OPEN
        if not self._is_authorized(chat_id, req_role):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        
        if self.userservice.is_owner(chat_id):
            
            #: inform user: owner cant leave
            self._send_text_msg(chat_id, text='You cant leave as the owner.')
            return

        if self.userservice.remove_user(chat_id):

            #: if userservice return True, user was removed
            self._send_text_msg(chat_id, text='You are no longer registered.')

        else:
            #: else, user was not registered
            self._send_text_msg(chat_id, text='You are not registered.')
            

    def mod_show_users_with_roles_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /users command - MOD

            Shows current users to the admin
        '''
        
        chat_id: int = update.effective_chat.id
        
        ### Check authorization ###
        req_role: Role = Role.MOD
        if not self._is_authorized(chat_id, req_role):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        
        context.bot.send_message(chat_id=update.effective_chat.id, text=self.userservice.users_as_str())
    
    def mod_show_banned_with_roles_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /banned command - MOD

            Shows current users to the admin
        '''
        
        chat_id: int = update.effective_chat.id
        
        ### Check authorization ###
        req_role: Role = Role.MOD
        if not self._is_authorized(chat_id, req_role):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        
        context.bot.send_message(chat_id=update.effective_chat.id, text=self.userservice.banned_as_str())
            
    def admin_create_token_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /token command - ADMIN
            Allows admins to create register-token
            
            #: handles a multi stage query for token creation
        '''

        chat_id: int = update.effective_chat.id
        query: CallbackQuery = update.callback_query
        
        ### Check authorization ###
        req_role: Role = Role.ADMIN
        if not self._is_authorized(chat_id, req_role):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return

        #: Start process
        if not query:

            #: get rank of current user
            user_role: Role = self.userservice.get_role_of(chat_id)

            #: build role option keyboard
            keyboard = [[InlineKeyboardButton(role.name.capitalize(), callback_data=role.value),] for role in Role if role > Role.OPEN and role < user_role]
            reply_markup = InlineKeyboardMarkup(keyboard)

            #: Send query for role options
            message: Message = update.message.reply_text("Choose the authority level for the token:", reply_markup=reply_markup)

            #: save payload
            self._add_query_payload(message.message_id, context, self.admin_create_token_command_callback, None, 1)

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
                
                #: update stage and save user selection for later in payload data
                payload.stage = 2
                payload.data = int(query.data)

                #: update query with days of validity options
                query.edit_message_text(text="Choose days of validity:")
                query.edit_message_reply_markup(reply_markup=reply_markup)
                
                return

            #: handle second user selection
            if payload.stage == 2:
                
                #: build token based on seletions
                token = self.userservice.generate_token(Role(payload.data), int(query.data))

                self.logger.debug('New {} token created'.format(token.role.name))
                
                #: inform user with new token
                query.edit_message_text('{} token is valid until {}'.format(token.role.name.capitalize(), token.valid_until.strftime('%y/%m/%d, %H:%M')))
                self._send_text_msg(chat_id, token.value)
                
                #: remove payload from context
                del context.bot_data[query.message.message_id]
                
                return 


    def admin_clear_tokens_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /clear command - ADMIN
        '''

        chat_id: int = update.effective_chat.id
        
        ### Check authorization ###
        req_role: Role = Role.ADMIN
        if not self._is_authorized(chat_id, req_role):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return

        self.userservice.clear_tokens()
        
    def admin_pause_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /pause command - ADMIN
        '''

        chat_id: int = update.effective_chat.id
        
        ### Check authorization ###
        req_role: Role = Role.ADMIN
        if not self._is_authorized(chat_id, req_role):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return

        if self.pause_unpause_callback(True):
            self._send_text_msg(chat_id, 'Surveillance deactivated.')
            
        else:
            self._send_text_msg(chat_id, 'Surveillance already inactive.')
        
    def admin_unpause_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /unpause command - ADMIN
        '''

        chat_id: int = update.effective_chat.id
        
        ### Check authorization ###
        req_role: Role = Role.ADMIN
        if not self._is_authorized(chat_id, req_role):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return

        if self.pause_unpause_callback(False):
            self._send_text_msg(chat_id, 'Surveillance activated.')
            
        else:
            self._send_text_msg(chat_id, 'Surveillance already active.')
        

    def admin_ban_user_command_callback(self, update: Update, context: CallbackContext) -> None:
        '''
        '''

        chat_id: int = update.effective_chat.id
        
        ### Check authorization ###
        req_role: Role = Role.ADMIN
        if not self._is_authorized(chat_id, req_role):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        
        self._admin_ban_unban_user_helper(update, context, self.admin_ban_user_command_callback, self.userservice.users, self.userservice.banned, 'banned')
        

    def admin_unban_user_command_callback(self, update: Update, context: CallbackContext) -> None:
        '''
        '''

        chat_id: int = update.effective_chat.id
        
        ### Check authorization ###
        req_role = Role.ADMIN
        if not self._is_authorized(chat_id, req_role):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return

        self._admin_ban_unban_user_helper(update, context, self.admin_unban_user_command_callback, self.userservice.banned, self.userservice.users, 'unbanned')

    def _admin_ban_unban_user_helper(self, update: Update, context: CallbackContext, callback: Callable, from_dict: UserDict, to_dict: UserDict, action_name: str) -> None:
        
        chat_id: int = update.effective_chat.id
        query: CallbackQuery = update.callback_query

        #: get rank of current user
        user_role: Role = self.userservice.get_role_of(chat_id)

        if not from_dict.with_lower_role(user_role):
            self._send_text_msg(chat_id, 'No options available.')
            return
        
        #: Start process
        if not query:
            
            #: get role of current user
            role: Role = self.userservice.users[chat_id].role
        
            #: build ban-unban-user option keyboard
            keyboard = [[InlineKeyboardButton(user.name, callback_data=user.chat_id)] for user in from_dict.with_lower_role(role).values()]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            #: send query
            message: Message = update.message.reply_text("Select the user to be {}:".format(action_name), reply_markup=reply_markup)
            
            self._add_query_payload(message.message_id, context, callback)
            
        #: If query exists, handle user selection
        else:
            
            self.logger.warn("User to be moved")
            
            #: If user not in from_dict, he cant be moved, abort
            if query.data not in from_dict:
                update.message.reply_text("User not found, aborting.")
                self.logger.warn("User not found, action aborted")
                return

            # TODO use userservice, required method references or other logic
            
            user_to_move: User = from_dict.pop(query.data)
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

        chat_id: int = update.effective_chat.id
        
        ### Check authorization ###
        req_role: Role = Role.OWNER
        if not self._is_authorized(chat_id, req_role):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        
        #: Clear users, banned users and tokens
        self.userservice.clear()


    def button(self, update: Update, context: CallbackContext) -> None:
        """Parses the CallbackQuery and updates the message text."""
        
        query: CallbackQuery = update.callback_query
        message_id: int = query.message.message_id

        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
        query.answer()

        #: abort if no handler is filed
        if message_id not in context.bot_data:
            #TODO handle error
            return

        #: delegate query data to filed handler method
        context.bot_data[message_id].callback(update, context)

    
    def alert(self, msg: str, req_role: Role = Role.OPEN) -> None:
        ''' Method to inform specified user group with custom message
        '''
        
        self._send_text_msg_to_lst(self.userservice.get_users().with_min_role(req_role), msg)
        
    def send_surveillance_video(self, video_path: str) -> None:
        ''' Sends the recorded surveillance video to every admin-user
        '''
        
        if not video_path:
            return

        #: Iterate admins and send video to each
        for chat_id in self.userservice.get_users().with_min_role(Role.ADMIN):
            self.updater.bot.send_video(chat_id=chat_id, video=open(video_path, 'rb'), supports_streaming=True,  caption=utils.basename(video_path))
    
    def _add_query_payload(self, message_id: int, context: CallbackContext, callback: Callable, data: object = None, stage: int = None) -> None:

        payload_dict = { message_id: Payload(data, stage, callback) }

        context.bot_data.update(payload_dict)

    def _is_authorized(self, chat_id: int, req_role: Role) -> bool:
        ''' Check if user with given chat_id is authorized for command

            #: chat_id                     - telegram chat_id
            #: command_authorization_level - required authorization level to execute command
        '''
        
        #: Banned chat_ids are never authorized
        if self.userservice.is_banned(chat_id):
            return False
        
        #: Command authorization level must be open, or the user has to be registered and own the required access rights
        return req_role is Role.OPEN or self.userservice.user_has_role(chat_id, req_role)
    
    def _send_text_msg_to_lst(self, lst: UserDict, text: str) -> None:
        ''' Sends message to list of chat_ids

            #: lst  - list of chat_ids
            #: text - message text
        '''
        
        #: Iterate over given list and send message to each user
        for user in lst: 
            self.updater.bot.send_message(chat_id=user, text=text)
    
    def _send_text_msg(self, chat_id: int, text: str) -> None:
        ''' Sends message to chat_id

            #: chat_id  - telegram chat_id
            #: text     - message text
        '''
        self.updater.bot.send_message(chat_id=chat_id, text=text)
