import pandas as pd
import numpy as np
import os
import json   


from dotenv import load_dotenv
load_dotenv()

OWNER_NAME = os.environ['OWNER_NAME']
MESSAGE_DIRECTORY = os.environ['MESSAGE_DIRECTORY']

MINUTES_IN_A_WEEK = 7*24*60

nameToAlias = {}
aliasCount = 0
def generate_alias(name):
    global aliasCount
    if name == OWNER_NAME:
        return name
    if name in nameToAlias:
        return "Person-"+str(nameToAlias[name])
    else:
        nameToAlias[name] = aliasCount
        aliasCount += 1
        return  "Person-"+str(nameToAlias[name])

def build_message_df(include_group_chats=True, hide_names=False):
    '''
    This function builds a dataframe from the JSON files in the specified directory.
    '''

    # Define the directory path
    directory_path = MESSAGE_DIRECTORY+'/messages/inbox'
    all_dirs = [d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]

    all_dfs = []
    # Loop through each directory and find files that match the pattern "message_*.json"
    for directory in all_dirs:
        current_dir_path = os.path.join(directory_path, directory)
        all_files_in_dir = os.listdir(current_dir_path)
        message_files = [f for f in all_files_in_dir if f.startswith('message_') and f.endswith('.json')]
        
        # Loop through the filtered files and read their contents
        for message_file in message_files:
            print(f'{round(100*(len(all_dfs)/len(all_dirs)), 2)}% of files read in', end='\r')
            with open(os.path.join(current_dir_path, message_file), 'r', encoding='utf-8') as file:
                data = json.load(file)
                df = pd.DataFrame(data['messages'])

                participants = set(map(lambda x: x['name'], data['participants']))
                if 'Facebook user' in participants:
                    continue

                participants_copy = participants.copy()
                if hide_names:
                    for p in participants_copy:
                        participants.remove(p)
                        participants.add(generate_alias(p))
                    df['sender_name'] = df['sender_name'].map(lambda x:generate_alias(x))
                    
                conversation_name = str(sorted(list(participants)))
                if 'content' not in df.columns:
                    continue
                df = df[['sender_name', 'timestamp_ms', 'content']]
                df['sendees'] = [participants.copy() for i in range(len(df))]
                df['conversation_name'] = conversation_name
                df.apply(lambda row: row['sendees'].remove(row['sender_name']) if row['sender_name'] in row['sendees'] else row['sendees'], axis=1)
                all_dfs.append(df)
    print(f'100% of files read in', end='\r')        
    full_df = pd.concat(all_dfs)

    ## clean df
    full_df['datetime'] = pd.to_datetime(full_df['timestamp_ms'], unit='ms')
    full_df['date'] = full_df['datetime'].dt.date

    if not include_group_chats:
        full_df = full_df[full_df['sendees'].map(lambda x: len(x) == 1)]

    return full_df

def get_message_counts(full_conversation_df):
    '''
    This function returns a dataframe with the number of messages sent by each person in the dataframe.
    '''
    def get_conversation_stats(df):
        total = df.shape[0]
        messages_from_me = df[df['sender_name'] == OWNER_NAME].shape[0]
        messages_from_other = total - messages_from_me
        message_count_data = pd.Series([total, messages_from_me, messages_from_other], index=['total', 'messages_from_me', 'messages_from_other'])
        return message_count_data

    message_count_per_day = full_conversation_df.groupby(['date','conversation_name']).apply(get_conversation_stats).reset_index()
    return message_count_per_day


def get_response_times_from_me(full_conversation_df):
    '''
    This method pulls my response times in minutes to others
    '''   
    def get_response_times_from_me_per_conversation(conversation_df):
        first_message = conversation_df[(conversation_df['sender_name'] == OWNER_NAME) & (conversation_df['sender_name'] != conversation_df['sender_name'].shift(1))]
        last_message = conversation_df[(conversation_df['sender_name'] != OWNER_NAME) & (conversation_df['sender_name'] != conversation_df['sender_name'].shift(-1))]
        first_and_last_message = pd.concat([first_message, last_message])

        first_and_last_message = first_and_last_message.sort_values(by='timestamp_ms')
        first_and_last_message['response_time_in_min'] = (first_and_last_message['timestamp_ms'].diff()+1)/1000/60
        first_and_last_message = first_and_last_message[first_and_last_message['sender_name'] == OWNER_NAME]

        return first_and_last_message

    full_conversation_df = full_conversation_df.sort_values(by=['conversation_name', 'timestamp_ms'])
    response_time_from_me_df = full_conversation_df.groupby('conversation_name').apply(get_response_times_from_me_per_conversation).reset_index(drop=True)
    return response_time_from_me_df

def get_response_times_to_me(full_conversation_df):
    '''
    This method pulls other's response times in minutes to me
    '''   
    def get_response_times_to_me_per_conversation(conversation_df):
        first_message = conversation_df[(conversation_df['sender_name'] != OWNER_NAME) & (conversation_df['sender_name'] != conversation_df['sender_name'].shift(1))]
        last_message = conversation_df[(conversation_df['sender_name'] == OWNER_NAME) & (conversation_df['sender_name'] != conversation_df['sender_name'].shift(-1))]
        first_and_last_message = pd.concat([first_message, last_message])

        first_and_last_message = first_and_last_message.sort_values(by='timestamp_ms')
        first_and_last_message['response_time_in_min'] = (first_and_last_message['timestamp_ms'].diff()+1)/1000/60
        first_and_last_message = first_and_last_message[first_and_last_message['sender_name'] != OWNER_NAME]

        return first_and_last_message
        
    full_conversation_df = full_conversation_df.sort_values(by=['conversation_name', 'timestamp_ms'])
    response_time_to_me_df = full_conversation_df.groupby('conversation_name').apply(get_response_times_to_me_per_conversation).reset_index(drop=True)
    return response_time_to_me_df

def get_ghost_pct(reponse_time_from_me_df, ghost_limit=MINUTES_IN_A_WEEK):
    '''
    This method calculates the percent of time my response time is greaters than the ghost limit
    '''
    ghost_pct = reponse_time_from_me_df[reponse_time_from_me_df.response_time_in_min > ghost_limit].shape[0]/reponse_time_from_me_df.shape[0]
    return ghost_pct

def get_comedian_rankings(full_conversation_df):
    '''Return a pandas series of how many times I have laughed with the other'''
    laughter_words = ['lol','lmao','haha']
    full_conversation_df['laughter_words'] = full_conversation_df['content'].map(lambda x: any(word in x.lower() for word in laughter_words) if type(x) == str else False)
    def get_comedy_score(conversation_df):
        num_laughs = conversation_df[conversation_df['sender_name'] == OWNER_NAME]['laughter_words'].sum()
        total_messages = conversation_df.shape[0]
        if total_messages < 100:
            return 0
        return 100*num_laughs/total_messages
    ranked_comedians = full_conversation_df.groupby('conversation_name').apply(get_comedy_score).sort_values(ascending=False)
    return ranked_comedians

def get_professor_rankings(full_conversation_df):
    '''Return a pandas series of how many questions I have asked the other person'''
    full_conversation_df['question_mark'] = full_conversation_df['content'].map(lambda x: '?' in x if type(x) == str else False)
    def get_professor_score(conversation_df):
        num_questions = conversation_df[conversation_df['sender_name'] == OWNER_NAME]['question_mark'].sum()
        total_messages = conversation_df.shape[0]
        if total_messages < 100:
            return 0
        return 100*num_questions/total_messages
    ranked_professors = full_conversation_df.groupby('conversation_name').apply(get_professor_score).sort_values(ascending=False)
    return ranked_professors