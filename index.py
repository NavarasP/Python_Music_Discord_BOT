import os
from youtube_search import YoutubeSearch
from queue import Queue
import pytube
from pytube import Playlist
import asyncio
import nextcord

from nextcord.ext import commands
import constants

intents = nextcord.Intents.all()
song_queue = Queue()
bot = commands.Bot(command_prefix="Alexa ", intents=intents)

is_playing = False
music_bot_channel_id=""
intents.voice_states = True
intents.members = True
intents.messages = True







def download_audio(video_url):
    youtube = pytube.YouTube(video_url)
    audio_stream = youtube.streams.filter(only_audio=True).first()
    audio_file_path = audio_stream.download()
    return audio_file_path
    
def delete_audio_file(file_path):
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Error while deleting audio file: {e}")





@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print('________________________________')


@bot.command(name='join')
async def join(ctx):
    
    if ctx.author.voice is None:
        await ctx.send("You are not in a voice channel.")
        return

    if ctx.voice_client is not None and ctx.voice_client.is_connected():
        await ctx.send("I am already in a voice channel.")
        return

    voice_channel = ctx.author.voice.channel
    await voice_channel.connect()
    await ctx.send(f"I have joined the voice channel {voice_channel}.")


async def add_to_queue(ctx,search_query):
    search_query=search_query
    if "youtube.com/playlist" in search_query:
        playlist_url = search_query
        playlist = Playlist(playlist_url)

        if not playlist.video_urls:
            await ctx.send("Playlist is empty or could not be fetched.")
            return

        for video_url in playlist.video_urls:
            song_queue.put(video_url)

        await ctx.send(f"Added {len(playlist.video_urls)} songs from the playlist to the queue.")

    else:
        if "youtube.com" in search_query or "youtu.be" in search_query:
            song_queue.put(search_query)
        else:
            results = YoutubeSearch(search_query, max_results=1).to_dict()

            if not results:
                await ctx.send("No search results found.")
                return

            video_url = "https://www.youtube.com" + results[0]['url_suffix']
            song_queue.put(video_url)
            await ctx.send(f"Added {results[0]['title']} to the queue.")



@bot.command(name='add')
async def add(ctx, *args):

    if not args:
        await ctx.send("Please provide a song name, search query, or playlist URL.")
        return
    search_query = " ".join(args)
    add_to_queue(ctx,search_query)



async def play_songfrom_queue(ctx):
    global is_playing
    while not song_queue.empty():
            song = song_queue.get()
            await ctx.send(f"Now playing: {song}")
            is_playing = True
            audio_file_path = download_audio(song)
            ctx.voice_client.play(nextcord.FFmpegOpusAudio(audio_file_path), after=lambda e: print(f'Player error: {e}') if e else None)
            while ctx.voice_client.is_playing():
                await asyncio.sleep(1)

            delete_audio_file(audio_file_path)
    is_playing = False



@bot.command(name='play', pass_context=True)
async def play(ctx, *, args=""):
    global is_playing
    if ctx.voice_client is None:
        if ctx.author.voice is None:
            await ctx.send("You are not in a voice channel.")
            return
        voice_channel = ctx.author.voice.channel
        await voice_channel.connect()

    if not args:
        if song_queue.empty():
            await ctx.send("The queue is empty. Use the `add` command to add songs to the queue.")
            is_playing = False
            return
        else:
            play_songfrom_queue(ctx)
            
    else:
        search_query = " ".join(args)
        add_to_queue(ctx,search_query)
        if not is_playing:
            play_songfrom_queue(ctx)
        
        
@bot.command(name='queue')
async def show_queue(ctx):
    if not song_queue:
        await ctx.send("The queue is empty. Use the `add` command to add songs to the queue.")
        return

    queue_text = "Current song queue:\n"
    for idx, song in enumerate(song_queue, start=1):
        queue_text += f"{idx}. {song}\n"

    await ctx.send(queue_text)


@bot.command(name='pause', pass_context=True)
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Playback paused.")
    else:
        await ctx.send("Nothing is currently playing.")

@bot.command(name='resume', pass_context=True)
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Playback resumed.")
    else:
        await ctx.send("Nothing to resume.")

@bot.command(name='skip')
async def skip(ctx):
    if ctx.voice_client is not None and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Skipped the current song.")
    else:
        await ctx.send("No song is currently playing.")

@bot.command(name='skipto')
async def skipto(ctx, index: int):
    global is_playing
    if index < 1 or index > len(song_queue):
        await ctx.send("Invalid song index.")
        return

    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    is_playing = False
    song_to_play = song_queue[index - 1]
    song_queue.remove(song_to_play)

    await play_songfrom_queue(ctx)
    


@bot.command(name='stop')
async def stop(ctx):
    global is_playing
    await ctx.voice_client.disconnect()
    is_playing=False
 

bot.run(constants.discordtocken)