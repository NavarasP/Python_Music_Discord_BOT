from nextcord.ui import View, Button
import nextcord
from nextcord.ext import commands
import index


intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="Alexa ", intents=intents)



Play=Button(style=nextcord.ButtonStyle.green,  emoji="⏯️",custom_id="play_pause")
Next=Button(style=nextcord.ButtonStyle.green,  emoji="⏭️", custom_id="stop")
Stop=Button(style=nextcord.ButtonStyle.green,  emoji="🛑", custom_id="next")
Vup=Button(style=nextcord.ButtonStyle.green,  emoji="🔊")
Vdn=Button(style=nextcord.ButtonStyle.green, emoji="🔉")
view =View()
view.add_item(Play)
view.add_item(Next)
view.add_item(Stop)
view.add_item(Vdn)
view.add_item(Vup)




async def controls_layout(ctx):
    global is_playing

    embed = nextcord.Embed(
        title="Button Demo",
        description="Click a button to trigger a function.",
        color=nextcord.Color.green()
    )
    
    
    

    async def play_callback( interaction: nextcord.Interaction):
        await interaction.response.defer()
        await play_command(interaction)

    # async def next_callback( interaction: nextcord.Interaction):
    #     await interaction.response.defer()
    #     await next_function(interaction)

    # async def stop_callback( interaction: nextcord.Interaction):
    #     await interaction.response.defer()
    #     await stop_function(interaction)

   




    Play.callback = play_callback
    # Next.callback = next_callback
    # Stop.callback = stop_callback
    



    await ctx.send(embed=embed, view=view)






    