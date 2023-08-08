import os
from youtube_search import YoutubeSearch
import spotipy
import pytube

from spotipy.oauth2 import SpotifyClientCredentials
from flask import Flask, request, jsonify

from queue import Queue
import asyncio




import nextcord
from nextcord.ext import commands

import constants



song_queue = Queue()
is_playing = False






intents = nextcord.Intents.all()
intents.voice_states = True
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} {bot.user.id}")
    print('___________________________________________')




@bot.command(name='join')
async def join(ctx):
    # Check if the user is in a voice channel
    if ctx.author.voice is None:
        await ctx.send("You are not in a voice channel.")
        return

    # Check if the bot is already in a voice channel
    if ctx.voice_client is not None and ctx.voice_client.is_connected():
        await ctx.send("I am already in a voice channel.")
        return

    # Join the user's voice channel
    voice_channel = ctx.author.voice.channel
    await voice_channel.connect()
    await ctx.send(f"I have joined the voice channel {voice_channel}.")



@bot.command(name='add')
async def add(ctx, *args):
    # Check if there are any arguments after !add
    if not args:
        await ctx.send("Please provide a song name or search query.")
        return

    # Join the arguments into a single search query
    search_query = " ".join(args)

    # Search for the video URLs based on the search query
    if "youtube.com" in search_query or "youtu.be" in search_query:
        song_queue.put(search_query)
    else:
        results = YoutubeSearch(search_query, max_results=5).to_dict()

        if not results:
            await ctx.send("No search results found.")
            return

        # Create a formatted list of the top 5 search results
        search_list = [f"{i+1}. {result['title']}" for i, result in enumerate(results)]

        # Send the list of search results to the user
        await ctx.send("\n".join(search_list))
        await ctx.send("Please select a number from the list (1-5) to add the song to the queue.")

        # Wait for the user's response (number 1 to 5)
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            user_response = await bot.wait_for('message', check=check, timeout=30)
            selected_number = int(user_response.content)

            if selected_number < 1 or selected_number > 5:
                await ctx.send("Invalid selection. Please select a number from 1 to 5.")
                return

            # Get the video URL of the selected song from the search results
            video_url = "https://www.youtube.com" + results[selected_number - 1]['url_suffix']

            # Add the video URL to the queue
            song_queue.put(video_url)
            await ctx.send(f"Added {results[selected_number - 1]['title']} to the queue.")
        
        except asyncio.TimeoutError:
            await ctx.send("No response received. Search operation cancelled.")
    global is_playing
    if not is_playing:
        await play(ctx)





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


@bot.command(name='play', pass_context=True)
async def play(ctx):
    global is_playing
    # Check if the bot is already playing audio
    if ctx.voice_client is None:
        # Check if the user is in a voice channel
        if ctx.author.voice is None:
            await ctx.send("You are not in a voice channel.")
            return

        # Join the user's voice channel
        voice_channel = ctx.author.voice.channel
        await voice_channel.connect()

    # Check if the queue is empty
    if song_queue.empty():
        await ctx.send("The queue is empty. Use the `add` command to add songs to the queue.")
        is_playing = False
        return

    # Play the first song in the queue
    while not song_queue.empty():
        # Play the first song in the queue
        song = song_queue.get()
        await ctx.send(f"Now playing: {song}")
        is_playing = True

        audio_file_path = download_audio(song)

        # Start audio streaming
        ctx.voice_client.play(nextcord.FFmpegOpusAudio(audio_file_path), after=lambda e: print(f'Player error: {e}') if e else None)

        # Wait for the song to finish playing
        while ctx.voice_client.is_playing():
            await asyncio.sleep(1)

        delete_audio_file(audio_file_path)

    is_playing=False
    
    
    












@bot.command(name='pause', pass_context=True)
async def pause(ctx):
    # Check if the bot is currently playing audio
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Playback paused.")
    else:
        await ctx.send("Nothing is currently playing.")

@bot.command(name='resume', pass_context=True)
async def resume(ctx):
    # Check if the bot is in a voice channel and paused
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Playback resumed.")
    else:
        await ctx.send("Nothing to resume.")









@bot.command(name='stop')
async def stop(ctx):
    await ctx.voice_client.disconnect()
 

bot.run(constants.discordtocken)


