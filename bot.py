import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, CallbackQueryHandler

import utils
import config as cfg
#from userservice import UserService
from user import User
from usertoken import Token

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

        #: Register cleartokens-command-handler
        admin_clear_tokens_command_handler = CommandHandler('cleartokens', self.admin_clear_tokens_command_callback)
        self.dispatcher.add_handler(admin_clear_tokens_command_handler)

        #: Register ban-command-handler
        admin_ban_user_command_handler = CommandHandler('ban', self.admin_ban_user_command_callback)
        self.dispatcher.add_handler(admin_ban_user_command_handler)

        #: Register unban-command-handler
        admin_unban_user_command_handler = CommandHandler('unban', self.admin_unban_user_command_callback)
        self.dispatcher.add_handler(admin_unban_user_command_handler)
        
        #: Register clear-command-handler
        owner_clear_all_users_and_admins_command_handler = CommandHandler('clear', self.owner_clear_all_users_and_admins_command_callback)
        self.dispatcher.add_handler(owner_clear_all_users_and_admins_command_handler)

        self.dispatcher.add_handler(CallbackQueryHandler(self.button))
        
        #: Init users and admin dict
        self.users = {}
        self.admins = {}
        self.banned = {}
        
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
        ###########################
        
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
        
        #: add as admin if token allows
        if token.role >= cfg.ROLE_TO_RANK[cfg.ADMIN_ROLE]:
            self.admins[chat_id] = user
        
        #: inform user
        self._send_text_msg(chat_id, text='Registered as {}!'.format(cfg.ROLES[cfg.RANK_TO_ROLE[token.role]]))

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
        ###########################
        
        if update.effective_chat.id in self.admins:
            context.bot.send_message(chat_id=update.effective_chat.id, text=self._get_all_users_as_text())
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Unauthorized!')
            
    def admin_create_token_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /token command - ADMIN

            Allows admins to create register-tokens.
            
            #: -a admin-token
            #: -m mod-token
            #: -s user-token
        '''
        chat_id = update.effective_chat.id
        
        ### Check authorization ###
        authorization_level = cfg.ROLE_TO_RANK[cfg.ADMIN_ROLE]
        if not self._is_authorized(chat_id, authorization_level):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        ###########################

        keyboard = [[InlineKeyboardButton(cfg.ROLES[cfg.RANK_TO_ROLE[i]], callback_data=i),] for i in range(1, 4)]

        reply_markup = InlineKeyboardMarkup(keyboard)

        message = update.message.reply_text("Choose the authority level for the token:", reply_markup=reply_markup)
        
        payload = { message.message_id: self.create_token_choose_days_of_validity }
        context.bot_data.update(payload)

        
        '''
        if not context.args or context.args[0] not in cfg.TOKEN_OPTIONS:
            self._send_text_msg(chat_id, 'Please use one of the options: -a for admin, -m for mod, -s for subscriber.')
            return
        
        role = cfg.TOKEN_OPTIONS[context.args[0]]
        
        if not self.users[chat_id].role > role:
            self._send_text_msg(chat_id, 'You can only generate tokens for roles lower than your own.')
            return
        
        if len(context.args) > 1 and not context.args[1].isnumeric():
            self._send_text_msg(chat_id, 'If you want to provide a period of validity, please use numeric values only. Default is 1 day.')
            return
        
        token = Token(role, context.args[1] if len(context.args) > 1 else 1)
        self.tokens[token.value] = token
        
        self._send_text_msg(chat_id, 'Newly created {role} token: {token}'.format(role = cfg.ROLES[cfg.RANK_TO_ROLE[role]], token = token.value))
        '''


    def admin_clear_tokens_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /cleartokens command - ADMIN
        '''

        chat_id = update.effective_chat.id
        
        ### Check authorization ###
        authorization_level = cfg.ROLE_TO_RANK[cfg.ADMIN_ROLE]
        if not self._is_authorized(chat_id, authorization_level):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        ###########################

        self.tokens.clear()

    def admin_ban_user_command_callback(self, update: Update, context: CallbackContext) -> None:
        '''
        '''

        chat_id = update.effective_chat.id
        
        ### Check authorization ###
        authorization_level = cfg.ROLE_TO_RANK[cfg.ADMIN_ROLE]
        if not self._is_authorized(chat_id, authorization_level):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        ###########################

        keyboard = [[InlineKeyboardButton(str(i*2), callback_data=str(i*2)), InlineKeyboardButton(str(i*2+1), callback_data=str(i*2+1))] for i in range(10)]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text("Choose user to ban:", reply_markup=reply_markup)

    def admin_unban_user_command_callback(self, update: Update, context: CallbackContext) -> None:
        '''
        '''

        chat_id = update.effective_chat.id
        
        ### Check authorization ###
        authorization_level = cfg.ROLE_TO_RANK[cfg.ADMIN_ROLE]
        if not self._is_authorized(chat_id, authorization_level):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        ###########################

        keyboard = [[InlineKeyboardButton(str(i*2), callback_data=str(i*2)), InlineKeyboardButton(str(i*2+1), callback_data=str(i*2+1))] for i in range(3)]

        reply_markup = InlineKeyboardMarkup(keyboard)

        message = update.message.reply_text("Choose user to unban:", reply_markup=reply_markup)

        print("MESSAGE_ID:", message.message_id)

        payload = {
            message.message_id: self.unban
        }
        context.bot_data.update(payload)
        
    def owner_clear_all_users_and_admins_command_callback(self, update: Update, context: CallbackContext) -> None:
        ''' Callback for the /clear command - OWNER

            Clears all users and admins except the owner
        '''

        chat_id = update.effective_chat.id
        
        ### Check authorization ###
        authorization_level = cfg.ROLE_TO_RANK[cfg.OWNER_ROLE]
        if not self._is_authorized(chat_id, authorization_level):
            self._send_text_msg(chat_id, 'Unauthorized!')
            return
        ###########################
        
        owner = self.users.pop(chat_id)
        
        self._send_text_msg_to_lst(self.users, 'Your subscription was terminated.')

        self.tokens.clear()
        
        self.admins.clear()
        self.users.clear()
        self.admins[chat_id] = owner
        self.users[chat_id] = owner


    def button(self, update: Update, context: CallbackContext) -> None:
        """Parses the CallbackQuery and updates the message text."""
        query = update.callback_query

        print("update:", update, "bot_data:", context.bot_data)

        print("context", query)

        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
        query.answer()

        query.edit_message_text(text=f"Selected option: {query.data}")

    
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
            self.updater.bot.send_video(chat_id=admin, video=open(video, 'rb'), supports_streaming=True,  caption=utils.basename(video))
    
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

    def create_token_choose_days_of_validity(self, update: Update, context: CallbackContext):

        keyboard = [
            [InlineKeyboardButton(1, callback_data=1), InlineKeyboardButton(3, callback_data=3)],
            [InlineKeyboardButton(5, callback_data=5), InlineKeyboardButton(10, callback_data=10)]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text("Choose days of validity:", reply_markup=reply_markup)

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

        lst = ['ID: {} - Username: {} - Role: {}'.format(u.chat_id, u.name, cfg.RANK_TO_ROLE[u.role]) for u in self.users]
        return '\n'.join(lst)
        
    
