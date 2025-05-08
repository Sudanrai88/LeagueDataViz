# -*- coding: utf-8 -*-
"""
Created on Thu May  1 13:33:01 2025

@author: SudanRai

Test data for future project / viz based on individual employee. Can be based on 1 - 1 metrics.
"""
import requests
import numpy as np
import pandas as pd
import time
import os


def get_account_data(api_key, summoner_name_dict):
    arr = []

    for key, value in summoner_name_dict.items():
        url = f'https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{key}/{value}'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://developer.riotgames.com",
            "X-Riot-Token": api_key
        }

        response = requests.get(url, headers=headers)
        print(response)
        puuid = response.json()["puuid"]

        arr.append(puuid)
    return arr


def get_match_ids(puuid_list, api_key, count):
    arr = []
    for puuid in puuid_list:
        url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://developer.riotgames.com",
            "X-Riot-Token": api_key
        }

        response = requests.get(url, headers=headers)

        df = response.json()
        arr.append(df)

    np_arr = np.array(arr)
    np_arr = np_arr.flatten()
    return np_arr


def get_match_data(arr, api_key):
    main_df = pd.DataFrame()
    count = 0

    for match in arr:
        url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://developer.riotgames.com",
            "X-Riot-Token": api_key
        }

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 125))
                print(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                response = requests.get(url, headers=headers)

            response.raise_for_status()  # Raises error for 4xx/5xx responses

            json_response = response.json()

            df = pd.json_normalize(
                json_response["info"],
                record_path=["participants"],
                meta=["gameDuration", "gameMode", "gameName", "gameVersion", "mapId", "platformId",
                      "gameId", "gameType", "gameStartTimestamp", "gameEndTimestamp", "gameCreation"],
                max_level=2
            )

            df2_temp = json_response["info"]["teams"]
            df2 = pd.json_normalize(df2_temp, sep='_', max_level=2)
            df = df.merge(df2, how="left", on="teamId")

            main_df = pd.concat([main_df, df])
            count += 1
            print(f"Match {count}: Data retrieved")

        except requests.exceptions.RequestException as e:
            print(f"RequestException for match {match}: {e}")
        except ValueError as e:
            print(f"ValueError for match {match}: {e}")
        except Exception as e:
            print(f"Unexpected error for match {match}: {e}")

        time.sleep(0.5)

    return main_df


def aggregate_classic(match_data, riotID, agg_account, data_dir):

    match_data = match_data.drop_duplicates(subset=["gameId", "puuid"])
    match_data = match_data[match_data["gameDuration"] > 600]
    match_data = match_data[match_data["gameMode"] == 'CLASSIC']
    #match_data = match_data[match_data["riotIdGameName"].isin(riotID)]
    match_data = match_data.replace({"riotIdGameName": agg_account})

    # Role assignment
    itemcolumn = ["item0", "item1", "item2", "item3", "item4", "item5", "item6"]
    jngcolumn = ["summoner1Id", "summoner2Id"]
    supp_items = [3865, 3866, 3867, 3877, 3869, 3870, 3876, 3871]
    smite_id = [11]

    mask_support = match_data[itemcolumn].isin(supp_items).any(axis=1)
    match_data["role"] = np.where(mask_support, "support", "other")

    mask_other = match_data["role"] == "other"
    mask_jungle = match_data.loc[mask_other, jngcolumn].isin(smite_id).any(axis=1)
    match_data.loc[mask_other, "role"] = np.where(mask_jungle, "jungle", "carry")

    # === Aggregation ===
    columns_to_drop = [
        'gameId', 'teamId', 'championName', 'summoner1Id', 'summoner2Id',
        'item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6'
    ]
    data_clean = match_data.drop(columns=columns_to_drop, errors='ignore')

    groupby_cols = ['riotIdGameName', 'role']
    grouped = data_clean.groupby(groupby_cols)

    agg_dict = {
        'win_y': ['count', lambda x: round(x.mean() * 100, 2)]
    }
    numeric_cols = data_clean.select_dtypes(include='number').columns

    for col in numeric_cols:
        if col not in groupby_cols + ['win_y']:
            agg_dict[col] = 'mean'

    df_agg = grouped.agg(agg_dict)
    df_agg.columns = [
        'games_played' if col[1] == 'count' else
        'win_percent' if col[1] == '<lambda>' else
        col[0] for col in df_agg.columns
    ]
    df_agg = df_agg.reset_index()

    # === Role-level Summary Rows ===
    role_summary_list = []

    for role in ['jungle', 'support', 'carry']:
        role_df = data_clean[data_clean['role'] == role]
        summary_stats = role_df[numeric_cols].mean().to_dict()
        summary_stats['games_played'] = role_df['win_y'].count()
        summary_stats['win_y'] = round(role_df['win_y'].mean() * 100, 2)
        summary_stats.update({'riotIdGameName': f'All_{role}', 'role': role})
        role_summary_list.append(summary_stats)

    summary_df = pd.DataFrame(role_summary_list)
    df_agg = pd.concat([df_agg, summary_df], ignore_index=True)

    # Save final aggregation
    final_output_path = os.path.join(data_dir, "classic_stats.csv")
    df_agg.to_csv(final_output_path, index=False)


def aggregate_aram(match_data, riotID, agg_account, data_dir):

    match_data = match_data.drop_duplicates(subset=["gameId", "puuid"])
    match_data = match_data[match_data["gameDuration"] > 300]
    match_data = match_data[match_data["gameMode"] == 'ARAM']
    #match_data = match_data[match_data["riotIdGameName"].isin(riotID)]
    match_data = match_data.replace({"riotIdGameName": agg_account})

    # === Aggregation ===
    columns_to_drop = [
        'gameId', 'teamId', 'championName', 'summoner1Id', 'summoner2Id',
        'item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6'
    ]
    data_clean = match_data.drop(columns=columns_to_drop, errors='ignore')

    groupby_cols = ['riotIdGameName']
    grouped = data_clean.groupby(groupby_cols)

    agg_dict = {
        'win_y': ['count', lambda x: round(x.mean() * 100, 2)]
    }
    numeric_cols = data_clean.select_dtypes(include='number').columns

    for col in numeric_cols:
        if col not in groupby_cols + ['win_y']:
            agg_dict[col] = 'mean'

    df_agg = grouped.agg(agg_dict)
    df_agg.columns = [
        'games_played' if col[1] == 'count' else
        'win_percent' if col[1] == '<lambda>' else
        col[0] for col in df_agg.columns
    ]
    df_agg = df_agg.reset_index()

    # === Role-level Summary Rows ===
    role_summary_list = []

    summary_stats = data_clean[numeric_cols].mean().to_dict()
    summary_stats['games_played'] = data_clean['win_y'].count()
    summary_stats['win_y'] = round(data_clean['win_y'].mean() * 100, 2)
    summary_stats.update({'riotIdGameName': 'All_aram', 'role': 'role'})
    role_summary_list.append(summary_stats)

    summary_df = pd.DataFrame(role_summary_list)
    df_agg = pd.concat([df_agg, summary_df], ignore_index=True)

    df_agg["role"] = "aram"

    # Save final aggregation
    final_output_path = os.path.join(data_dir, "aram_stats.csv")
    df_agg.to_csv(final_output_path, index=False)
