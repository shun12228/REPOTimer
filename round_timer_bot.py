import discord
from discord.ext import commands
import asyncio
import os
from discord import FFmpegPCMAudio
import re
from discord import app_commands

TOKEN = ''

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

class MyClient(commands.Bot):
    async def setup_hook(self):
        await self.tree.sync()

bot = MyClient(command_prefix="!", intents=intents)

# Discord VCで再生（Voiceフォルダのmp3ファイルを再生）
async def play_voice_file(channel, filename, voice_client):
    filepath = os.path.join(os.path.dirname(__file__), "Voice", filename)
    if voice_client.is_playing():
        voice_client.stop()
        await asyncio.sleep(0.1)
    audio = FFmpegPCMAudio(filepath)
    voice_client.play(audio)
    while voice_client.is_playing():
        await asyncio.sleep(0.5)
    return voice_client

# 音声再生を非同期で行う関数
async def play_voice_file_async(channel, filename, voice_client):
    filepath = os.path.join(os.path.dirname(__file__), "Voice", filename)
    if voice_client.is_playing():
        voice_client.stop()
        await asyncio.sleep(0.1)
    audio = FFmpegPCMAudio(filepath)
    voice_client.play(audio)

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client and ctx.voice_client.is_connected():
            await ctx.send("すでにボイスチャンネルに参加しています。")
        else:
            await channel.connect()
            await ctx.send(f"{channel.name} に参加しました。")
    else:
        await ctx.send("ボイスチャンネルに参加してからコマンドを実行してください。")

# 前回のタイマー用メッセージIDを保存する変数
last_timer_message = {"id": None, "channel_id": None}

@bot.command()
async def roundstart(ctx, time: str = "50m"):
    global last_timer_message

    # 前回のタイマー用メッセージがあれば削除
    if last_timer_message["id"] and last_timer_message["channel_id"]:
        try:
            channel = bot.get_channel(last_timer_message["channel_id"])
            msg = await channel.fetch_message(last_timer_message["id"])
            await msg.delete()
        except Exception:
            pass  # メッセージが既に消えている場合などは無視

    m = re.match(r"^(\d+)([ms]?)$", time) if not time.isdigit() else re.match(r"^(\d+)$", time)
    if not m:
        m = re.match(r"^(\d+)([ms]?)$", time)
    if not m:
        await ctx.send("時間指定は 10m や 90s のようにしてください（例: !roundstart 15m）")
        return
    value, unit = m.groups() if len(m.groups()) == 2 else (m.group(1), "m")
    value = int(value)
    if unit == "s":
        seconds = value
    else:
        seconds = value * 60
    notify_points = [40*60, 30*60, 20*60, 10*60, 5*60, 60, 10]
    notify_points = [p for p in notify_points if p < seconds]
    notify_points = [seconds] + sorted(set(notify_points), reverse=True)
    bot._timer_cancel = False
    voice_client = ctx.voice_client if ctx.voice_client and ctx.voice_client.is_connected() else None
    if not voice_client:
        await ctx.send("先に !join でボイスチャンネルにBotを参加させてください。")
        return
    channel = voice_client.channel

    # 残り時間のテキストを生成
    def format_time(sec):
        m, s = divmod(sec, 60)
        if m > 0:
            return f"{m}分{s}秒" if s > 0 else f"{m}分"
        else:
            return f"{s}秒"

    file_map = {
        50*60: "timer_start.mp3",
        49*60: "timer_start_49m.mp3",
        48*60: "timer_start_48m.mp3",
        47*60: "timer_start_47m.mp3",
        46*60: "timer_start_46m.mp3",
        45*60: "timer_start_45m.mp3",
        44*60: "timer_start_44m.mp3",
        43*60: "timer_start_43m.mp3",
        42*60: "timer_start_42m.mp3",
        41*60: "timer_start_41m.mp3",
        40*60: "timer_start_40m.mp3",
        40*60: "remain_40m.mp3",
        30*60: "remain_30m.mp3",
        20*60: "remain_20m.mp3",
        10*60: "remain_10m.mp3",
        5*60: "remain_5m.mp3",
        60: "remain_1m.mp3",
        10: "remain_10s.mp3",
        9: "remain_9s.mp3",
        8: "remain_8s.mp3",
        7: "remain_7s.mp3",
        6: "remain_6s.mp3",
        5: "remain_5s.mp3",
        4: "remain_4s.mp3",
        3: "remain_3s.mp3",
        2: "remain_2s.mp3",
        1: "remain_1s.mp3",
        0: "end.mp3",
    }

    # メッセージ送信＆オブジェクト取得
    msg = await ctx.send(f"タイマーを開始しました　**{format_time(seconds)}**")

    # 新しいメッセージIDとチャンネルIDを保存
    last_timer_message["id"] = msg.id
    last_timer_message["channel_id"] = msg.channel.id

    current = seconds
    # 開始時の音声ファイルを取得
    if seconds in file_map:
        start_voice = file_map[seconds]
    elif seconds >= 40 * 60:
        start_voice = "timer_start.mp3"
    else:
        start_voice = "timer_start_39m.mp3"
    asyncio.create_task(play_voice_file_async(channel, start_voice, voice_client))

    # 通常の通知ポイント
    for prev, point in zip(notify_points, notify_points[1:]):
        wait_time = prev - point
        # 10秒以下のカウントダウン直前まで通常ループ
        if point > 10:
            for _ in range(wait_time):
                if getattr(bot, '_timer_cancel', False):
                    await msg.edit(content="タイマーが中断されました。")
                    asyncio.create_task(play_voice_file_async(channel, "end.mp3", voice_client))
                    return
                current -= 1
                await msg.edit(content=f"タイマーを開始しました　**{format_time(current)}**")
                await asyncio.sleep(1)
            fname = file_map.get(point)
            if fname:
                asyncio.create_task(play_voice_file_async(channel, fname, voice_client))
        else:
            # 10秒以下になったらbreakしてカウントダウンへ
            break

    # --- 追加ここから ---
    # currentが10秒より大きい場合、10秒になるまで1秒ずつカウントダウン
    while current > 10:
        if getattr(bot, '_timer_cancel', False):
            await msg.edit(content="タイマーが中断されました。")
            asyncio.create_task(play_voice_file_async(channel, "end.mp3", voice_client))
            return
        current -= 1
        await msg.edit(content=f"タイマーを開始しました　**{format_time(current)}**")
        await asyncio.sleep(1)
    # --- 追加ここまで ---

    # 10秒以下のカウントダウン（10〜1秒）
    for sec in range(min(current, 10), 0, -1):
        if getattr(bot, '_timer_cancel', False):
            await msg.edit(content="タイマーが中断されました。")
            asyncio.create_task(play_voice_file_async(channel, "end.mp3", voice_client))
            return
        fname = file_map.get(sec)
        if fname:
            asyncio.create_task(play_voice_file_async(channel, fname, voice_client))
        current -= 1
        await msg.edit(content=f"タイマーを開始しました　**{format_time(current)}**")
        await asyncio.sleep(1)

    asyncio.create_task(play_voice_file_async(channel, "end.mp3", voice_client))
    await msg.edit(content="タイマーが終了しました。")

@bot.command()
async def leave(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect(force=True)
        await ctx.send("ボイスチャンネルから退出しました。")
    else:
        await ctx.send("Botはボイスチャンネルに参加していません。")

@bot.command()
async def roundstop(ctx):
    bot._timer_cancel = True
    await ctx.send("タイマー停止リクエストを受け付けました。")

# --- スラッシュコマンド用のタイマー処理 ---
@bot.tree.command(name="timer", description="タイマーを開始します（例: /timer 1m）")
@app_commands.describe(time="タイマー時間（例: 1m, 30s, 10m など）")
async def timer(interaction: discord.Interaction, time: str = "50m"):
    # --- パース処理 ---
    m = re.match(r"^(\d+)([ms]?)$", time) if not time.isdigit() else re.match(r"^(\d+)$", time)
    if not m:
        m = re.match(r"^(\d+)([ms]?)$", time)
    if not m:
        await interaction.response.send_message("時間指定は 10m や 90s のようにしてください（例: /timer 15m）", ephemeral=True)
        return
    value, unit = m.groups() if len(m.groups()) == 2 else (m.group(1), "m")
    value = int(value)
    if unit == "s":
        seconds = value
    else:
        seconds = value * 60

    # --- ボイスチャンネル取得 ---
    voice_client = interaction.guild.voice_client
    if not voice_client or not voice_client.is_connected():
        await interaction.response.send_message("先に /j でボイスチャンネルにBotを参加させてください。", ephemeral=True)
        return
    channel = voice_client.channel

    # --- 残り時間のテキストを生成 ---
    def format_time(sec):
        m, s = divmod(sec, 60)
        if m > 0:
            return f"{m}分{s}秒" if s > 0 else f"{m}分"
        else:
            return f"{s}秒"

    file_map = {
        50*60: "timer_start.mp3",
        49*60: "timer_start_49m.mp3",
        48*60: "timer_start_48m.mp3",
        47*60: "timer_start_47m.mp3",
        46*60: "timer_start_46m.mp3",
        45*60: "timer_start_45m.mp3",
        44*60: "timer_start_44m.mp3",
        43*60: "timer_start_43m.mp3",
        42*60: "timer_start_42m.mp3",
        41*60: "timer_start_41m.mp3",
        40*60: "timer_start_40m.mp3",
        40*60: "remain_40m.mp3",
        30*60: "remain_30m.mp3",
        20*60: "remain_20m.mp3",
        10*60: "remain_10m.mp3",
        5*60: "remain_5m.mp3",
        60: "remain_1m.mp3",
        10: "remain_10s.mp3",
        9: "remain_9s.mp3",
        8: "remain_8s.mp3",
        7: "remain_7s.mp3",
        6: "remain_6s.mp3",
        5: "remain_5s.mp3",
        4: "remain_4s.mp3",
        3: "remain_3s.mp3",
        2: "remain_2s.mp3",
        1: "remain_1s.mp3",
        0: "end.mp3",
    }

    notify_points = [40*60, 30*60, 20*60, 10*60, 5*60, 60, 10]
    notify_points = [p for p in notify_points if p < seconds]
    notify_points = [seconds] + sorted(set(notify_points), reverse=True)
    bot._timer_cancel = False

    # --- メッセージ送信＆取得 ---
    await interaction.response.send_message(f"タイマーを開始しました　**{format_time(seconds)}**")
    msg = await interaction.original_response()

    current = seconds
    # 開始時の音声ファイルを取得
    if seconds in file_map:
        start_voice = file_map[seconds]
    elif seconds >= 40 * 60:
        start_voice = "timer_start.mp3"
    else:
        start_voice = "timer_start_39m.mp3"
    asyncio.create_task(play_voice_file_async(channel, start_voice, voice_client))

    # 通常の通知ポイント
    for prev, point in zip(notify_points, notify_points[1:]):
        wait_time = prev - point
        if point > 10:
            for _ in range(wait_time):
                if getattr(bot, '_timer_cancel', False):
                    await msg.edit(content="タイマーが中断されました。")
                    asyncio.create_task(play_voice_file_async(channel, "end.mp3", voice_client))
                    return
                current -= 1
                await msg.edit(content=f"タイマーを開始しました　**{format_time(current)}**")
                await asyncio.sleep(1)
            fname = file_map.get(point)
            if fname:
                asyncio.create_task(play_voice_file_async(channel, fname, voice_client))
        else:
            break

    while current > 10:
        if getattr(bot, '_timer_cancel', False):
            await msg.edit(content="タイマーが中断されました。")
            asyncio.create_task(play_voice_file_async(channel, "end.mp3", voice_client))
            return
        current -= 1
        await msg.edit(content=f"タイマーを開始しました　**{format_time(current)}**")
        await asyncio.sleep(1)

    for sec in range(min(current, 10), 0, -1):
        if getattr(bot, '_timer_cancel', False):
            await msg.edit(content="タイマーが中断されました。")
            asyncio.create_task(play_voice_file_async(channel, "end.mp3", voice_client))
            return
        fname = file_map.get(sec)
        if fname:
            asyncio.create_task(play_voice_file_async(channel, fname, voice_client))
        current -= 1
        await msg.edit(content=f"タイマーを開始しました　**{format_time(current)}**")
        await asyncio.sleep(1)

    asyncio.create_task(play_voice_file_async(channel, "end.mp3", voice_client))
    await msg.edit(content="タイマーが終了しました。")

# スラッシュコマンドで/join → /j
@bot.tree.command(name="j", description="ボイスチャンネルに参加します")
async def j(interaction: discord.Interaction):
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        if interaction.guild.voice_client and interaction.guild.voice_client.is_connected():
            await interaction.response.send_message("既に参加しています。", ephemeral=True)
        else:
            await channel.connect()
            await interaction.response.send_message(f"{channel.name} に参加しました。", ephemeral=True)
    else:
        await interaction.response.send_message("先にボイスチャンネルへ参加してください。", ephemeral=True)

# スラッシュコマンドで/leave → /e
@bot.tree.command(name="e", description="ボイスチャンネルから退出します")
async def e(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect(force=True)
        await interaction.response.send_message("ボイスチャンネルから退出しました。", ephemeral=True)
    else:
        await interaction.response.send_message("Botはボイスチャンネルに参加していません。", ephemeral=True)

# 既存の roundstart 関数はそのまま利用できます

if __name__ == "__main__":
    bot.run(TOKEN)