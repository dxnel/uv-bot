import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import time
import Paginator
import asyncio
import json
import requests
import base64
import re

intents = discord.Intents.default()
intents.messages = True  
intents.message_content = True  
intents.members = True
intents.presences = True
intents.guild_scheduled_events = True

bot = commands.Bot(command_prefix='uv!', intents=intents)
version = "1.0.0-rc2 [290324]"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('/help｜ultraviolet [uv]'))
    embed = discord.Embed(description=f"[uv]bot est à présent en ligne et prêt à être utilisé", color=discord.Color.from_rgb(193,168,233))
    embed.set_author(name=bot.user.display_name, icon_url=bot.user.avatar)
    embed.add_field(name="Version", value=f"{version}", inline=False)
    config = load_config() 
    log_channel_id = config.get('log_channel') 
    if log_channel_id:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(embed=embed)
        else:
            print("Le salon de logging n'existe pas.")
    else:
        print("Le salon de logging n'a pas été défini.")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
        
@bot.event
async def on_message(message):
    if "y/n" in message.content:
        await message.add_reaction('⬆️')
        await message.add_reaction('⬇️')
    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    embed = discord.Embed(description=f"Message supprimé sur {message.channel.jump_url}", color=discord.Color.red())
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar)
    embed.add_field(name="Auteur du message", value=f"{message.author} `({message.author.id})`", inline=False)
    embed.set_footer(text=f"ID : {message.id}")
    embed.add_field(name="Contenu du message", value=message.content if message.content else "Contenu inconnu", inline=False)
    
    send_time = f"<t:{int(message.created_at.timestamp())}:F>"
    embed.add_field(name="Date d'envoi", value=send_time, inline=False)
    
    config = load_config() 
    log_channel_id = config.get('log_channel') 
    if log_channel_id:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(embed=embed)
        else:
            print("Le salon de logging n'existe pas.")
    else:
        print("Le salon de logging n'a pas été défini.")

@bot.event
async def on_message_edit(before, after):
    if before.content != after.content:
        embed = discord.Embed(description=f"Message modifié sur {after.channel.jump_url}", color=discord.Color.from_rgb(193,168,233))
        embed.set_author(name=after.author.display_name, icon_url=after.author.avatar)
        embed.add_field(name="Auteur du message", value=f"{after.author} `({after.author.id})`", inline=False)
        embed.set_footer(text=f"ID : {after.id}")
        embed.add_field(name="Nouveau contenu", value=after.content, inline=False)
        embed.add_field(name="Ancien contenu", value=before.content, inline=False)
        send_time = f"<t:{int(before.created_at.timestamp())}:F>"
        embed.add_field(name="Date d'envoi", value=send_time, inline=False)
        
        config = load_config() 
        log_channel_id = config.get('log_channel') 
        if log_channel_id:
            log_channel = bot.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)
            else:
                print("Le salon de logging n'existe pas.")
        else:
            print("Le salon de logging n'a pas été défini.")

@bot.event
async def on_member_update(before, after):
    added_roles = set(after.roles) - set(before.roles)
    removed_roles = set(before.roles) - set(after.roles)
    if before.display_name != after.display_name:
        embed = discord.Embed(description=f"{after.mention} `({after.name})` a été mis à jour", color=discord.Color.from_rgb(193,168,233))
        embed.set_author(name=after.display_name, icon_url=after.avatar)
        embed.add_field(name="Nouveau pseudo", value=after.display_name, inline=False)
        embed.add_field(name="Ancien pseudo", value=before.display_name, inline=False)
        embed.add_field(name="Date de modification", value=f"<t:{int(time.time())}:F>", inline=False)
        embed.set_footer(text=f"ID : {after.id}")
        
        config = load_config() 
        log_channel_id = config.get('log_channel') 
        if log_channel_id:
            log_channel = bot.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)
            else:
                print("Le salon de logging n'existe pas.")
        else:
            print("Le salon de logging n'a pas été défini.")

    if added_roles:
        for role in added_roles:
            embed = discord.Embed(description=f"{after.mention} a été attribué le rôle {role.mention}", color=discord.Color.green())
            embed.set_author(name=after.display_name, icon_url=after.avatar)
            embed.set_footer(text=f"ID : {after.id}")
            embed.add_field(name="Date de création", value=f"<t:{int(role.created_at.timestamp())}:F>", inline=False)

            config = load_config()
            log_channel_id = config.get('log_channel')
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")

    if removed_roles:
        for role in removed_roles:
            embed = discord.Embed(description=f"{after.mention} a été retiré le rôle {role.mention}", color=discord.Color.red())
            embed.set_author(name=after.display_name, icon_url=after.avatar)
            embed.set_footer(text=f"ID : {after.id}")
            embed.add_field(name="Date de création", value=f"<t:{int(role.created_at.timestamp())}:F>", inline=False)

            config = load_config()
            log_channel_id = config.get('log_channel')
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")
    if before.timed_out_until is None:
        if after.timed_out_until is not None:
            embed = discord.Embed(description=f"{after.mention} a été exclu", color=discord.Color.red())
            embed.set_author(name=after.display_name, icon_url=after.avatar)
            embed.set_footer(text=f"ID : {after.id}")
            embed.add_field(name="Date d'expiration", value=f"<t:{int(after.timed_out_until.timestamp())}:F>", inline=False)
            embed.add_field(name="Date d'arrivée", value=f"<t:{int(after.joined_at.timestamp())}:F>", inline=False)

            config = load_config()
            log_channel_id = config.get('log_channel')
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")
                
    if before.timed_out_until is not None:
        if after.timed_out_until is None:
            embed = discord.Embed(description=f"{after.mention} n'est plus exclu", color=discord.Color.green())
            embed.set_author(name=after.display_name, icon_url=after.avatar)
            embed.set_footer(text=f"ID : {after.id}")
            embed.add_field(name="Date d'arrivée", value=f"<t:{int(after.joined_at.timestamp())}:F>", inline=False)

            config = load_config()
            log_channel_id = config.get('log_channel')
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")
            
@bot.event
async def on_guild_channel_update(before, after):
    if isinstance(after, discord.TextChannel) and before.overwrites != after.overwrites:
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.overwrite_update): 
            if entry.target == after:
                embed = discord.Embed(description=f"Les permissions du salon {after.mention} ont été modifiées.", color=discord.Color.from_rgb(193,168,233))
                embed.set_footer(text=f"ID : {after.guild.id}")
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.add_field(name="Date de création", value=f"<t:{int(after.created_at.timestamp())}:F>", inline=False)
        
                config = load_config() 
                log_channel_id = config.get('log_channel') 
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break
    if isinstance(before, discord.CategoryChannel) and before.overwrites != after.overwrites:
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.overwrite_update):
            if entry.target == after:
                embed = discord.Embed(description=f"Les permissions de la catégorie {after.mention} ont été modifiées.", color=discord.Color.from_rgb(193,168,233))
                embed.set_footer(text=f"ID : {after.guild.id}")
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.add_field(name="Date de création", value=f"<t:{int(after.created_at.timestamp())}:F>", inline=False)
        
                config = load_config() 
                log_channel_id = config.get('log_channel') 
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break
    if before.name != after.name and isinstance(after, discord.TextChannel):
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.channel_update):
            if entry.target == after:
                embed = discord.Embed(description=f"Le salon {after.mention} a été renommé", color=discord.Color.from_rgb(193,168,233))
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.set_footer(text=f"ID : {after.id}")
                embed.add_field(name="Nouveau nom", value=after.name, inline=False)
                embed.add_field(name="Ancien nom", value=before.name, inline=False)
                embed.add_field(name="Date de création", value=f"<t:{int(after.created_at.timestamp())}:F>", inline=False)
        
                config = load_config() 
                log_channel_id = config.get('log_channel') 
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break
    if before.name != after.name and isinstance(after, discord.VoiceChannel):
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.channel_update):
            if entry.target == after:
                embed = discord.Embed(description=f"Le salon {after.mention} a été renommé", color=discord.Color.from_rgb(193,168,233))
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.set_footer(text=f"ID : {after.id}")
                embed.add_field(name="Nouveau nom", value=after.name, inline=False)
                embed.add_field(name="Ancien nom", value=before.name, inline=False)
                embed.add_field(name="Date de création", value=f"<t:{int(after.created_at.timestamp())}:F>", inline=False)
        
                config = load_config() 
                log_channel_id = config.get('log_channel') 
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break
    elif isinstance(after, discord.CategoryChannel) and before.name != after.name:
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.channel_update):
            if entry.target == after:
                embed = discord.Embed(description=f"La catégorie {after.mention} a été renommée", color=discord.Color.from_rgb(193, 168, 233))
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.set_footer(text=f"ID : {after.id}")
                embed.add_field(name="Nouveau nom", value=after.name, inline=False)
                embed.add_field(name="Ancien nom", value=before.name, inline=False)
                embed.add_field(name="Date de création", value=f"<t:{int(after.created_at.timestamp())}:F>", inline=False)

                config = load_config()
                log_channel_id = config.get('log_channel')
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break
@bot.event
async def on_user_update(before, after):
    config = load_config() 
    log_channel_id = config.get('log_channel') 
    if before.avatar != after.avatar:
        embed = discord.Embed(description=f"{after.mention} `({after.name})` a mis à jour son profil", color=discord.Color.from_rgb(193, 168, 233))
        embed.set_author(name=after.name, icon_url=after.avatar.url)
        embed.set_thumbnail(url=after.avatar.url)
        download_link = f"[Lien de l'image]({after.avatar.url})"
        embed.add_field(name="", value=download_link)
        embed.set_footer(text=f"ID : {after.id}")
        embed.add_field(name="Date de création", value=f"<t:{int(after.created_at.timestamp())}:F>", inline=False)
        
        config = load_config() 
        log_channel_id = config.get('log_channel') 
        if log_channel_id:
            log_channel = bot.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)
            else:
                print("Le salon de logging n'existe pas.")
        else:
            print("Le salon de logging n'a pas été défini.")

@bot.event
async def on_guild_update(before, after):
    if before.icon != after.icon:
        async for entry in after.audit_logs(action=discord.AuditLogAction.guild_update):
            if entry.target == after:
                embed = discord.Embed(description=f"Le serveur {after.name} a été mise à jour", color=discord.Color.from_rgb(193, 168, 233))
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.set_footer(text=f"ID : {after.id}")
                embed.set_thumbnail(url=after.icon.url)
                download_link = f"[Lien de l'image]({after.icon.url})"
                embed.add_field(name="Nouvelle icône", value=download_link, inline=False)
                embed.add_field(name="Date de création", value=f"<t:{int(after.created_at.timestamp())}:F>", inline=False)

                config = load_config()
                log_channel_id = config.get('log_channel')
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break
    
    if before.name != after.name:
        async for entry in after.audit_logs(limit=1, action=discord.AuditLogAction.guild_update):
            author = entry.user
            embed = discord.Embed(description=f"Le serveur {after.name} a été mise à jour", color=discord.Color.from_rgb(193, 168, 233))
            embed.set_thumbnail(url=after.icon.url)
            embed.set_author(name=author.display_name, icon_url=author.avatar)
            embed.set_footer(text=f"ID : {before.id}")
            embed.add_field(name="Nouveau nom", value=after.name, inline=False)
            embed.add_field(name="Ancien nom", value=before.name, inline=False)
            embed.add_field(name="Date de modification", value=f"<t:{int(time.time())}:F>", inline=False)

            config = load_config()
            log_channel_id = config.get('log_channel')
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")
            break

@bot.event
async def on_guild_channel_delete(channel):
    if not isinstance(channel, discord.CategoryChannel):
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete):
            if entry.target.id == channel.id:
                embed = discord.Embed(description=f"Le salon `{channel.name}` a été supprimé", color=discord.Color.red())
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.set_footer(text=f"ID : {channel.id}")
                embed.add_field(name="Date de suppression", value=f"<t:{int(time.time())}:F>", inline=False)

                config = load_config()
                log_channel_id = config.get('log_channel')
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break
    else:
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete):
            if entry.target.id == channel.id:
                embed = discord.Embed(description=f"La catégorie `{channel.name}` a été supprimée", color=discord.Color.red())
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.set_footer(text=f"ID : {channel.id}")
                embed.add_field(name="Date de suppression", value=f"<t:{int(time.time())}:F>", inline=False)

                config = load_config()
                log_channel_id = config.get('log_channel')
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break

@bot.event
async def on_guild_channel_create(channel):
    if not isinstance(channel, discord.CategoryChannel):
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create):
            if entry.target.id == channel.id:
                category_name = "Aucune"
                category_position = "Aucune"
                if channel.category:
                    category_name = channel.category.name
                    category_position = channel.category.position
                embed = discord.Embed(description=f"Le salon {channel.mention} a été créé", color=discord.Color.green())
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.set_footer(text=f"ID : {channel.id}")
                embed.add_field(name="Catégorie", value=category_name, inline=False)
                embed.add_field(name="Emplacement", value=category_position, inline=False)
                embed.add_field(name="Date de création", value=f"<t:{int(time.time())}:F>", inline=False)

                config = load_config()
                log_channel_id = config.get('log_channel')
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break
    else:
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create):
            if entry.target.id == channel.id:
                embed = discord.Embed(description=f"La catégorie `{channel.name}` a été créée", color=discord.Color.green())
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.set_footer(text=f"ID : {channel.id}")
                embed.add_field(name="Date de création", value=f"<t:{int(time.time())}:F>", inline=False)

                config = load_config()
                log_channel_id = config.get('log_channel')
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break

@bot.event
async def on_member_join(member):
    embed = discord.Embed(description=f"{member.mention} a rejoint le serveur", color=discord.Color.green())
    embed.set_author(name=member.display_name, icon_url=member.avatar)
    embed.set_footer(text=f"ID : {member.id}")
    embed.add_field(name="Date de création du compte", value=f"<t:{int(member.created_at.timestamp())}:F>", inline=False)
    embed.add_field(name="Date d'arrivée", value=f"<t:{int(time.time())}:F>", inline=False)
    embed.add_field(name="Nombre de membres", value=len(member.guild.members), inline=False)

    config = load_config()
    log_channel_id = config.get('log_channel')
    if log_channel_id:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(embed=embed)
        else:
            print("Le salon de logging n'existe pas.")
    else:
        print("Le salon de logging n'a pas été défini.")

@bot.event
async def on_member_remove(member):
    embed = discord.Embed(description=f"{member.mention} a quitté le serveur", color=discord.Color.red())
    embed.set_author(name=member.display_name, icon_url=member.avatar)
    embed.set_footer(text=f"ID : {member.id}")
    embed.add_field(name="Date d'arrivée", value=f"<t:{int(member.joined_at.timestamp())}:F>", inline=False)
    embed.add_field(name="Date de départ", value=f"<t:{int(time.time())}:F>", inline=False)

    config = load_config()
    log_channel_id = config.get('log_channel')
    if log_channel_id:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(embed=embed)
        else:
            print("Le salon de logging n'existe pas.")
    else:
        print("Le salon de logging n'a pas été défini.")

@bot.event
async def on_member_ban(guild, user):
    async for entry in guild.audit_logs(action=discord.AuditLogAction.ban):
        if entry.target.id == user.id:
            embed = discord.Embed(description=f"{user.mention} a été banni du serveur", color=discord.Color.red())
            embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
            embed.set_footer(text=f"ID : {user.id}")
            embed.add_field(name="Raison du bannissement", value=entry.reason if entry.reason else "Aucune raison spécifiée", inline=False)
            embed.add_field(name="Date du bannissement", value=f"<t:{int(time.time())}:F>", inline=False)

            config = load_config()
            log_channel_id = config.get('log_channel')
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")
            break

@bot.event
async def on_member_unban(guild, user):
    async for entry in guild.audit_logs(action=discord.AuditLogAction.unban):
        if entry.target.id == user.id:
            embed = discord.Embed(description=f"{user.mention} a été débanni du serveur", color=discord.Color.green())
            embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
            embed.set_footer(text=f"ID : {user.id}")
            embed.add_field(name="Date du débannissement", value=f"<t:{int(time.time())}:F>", inline=False)

            config = load_config()
            log_channel_id = config.get('log_channel')
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")
            break

@bot.event
async def on_guild_role_create(role):
    async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_create):
        if entry.target.id == role.id:
            embed = discord.Embed(description=f"Le rôle {role.mention} a été créé", color=discord.Color.green())
            embed.set_footer(text=f"ID du rôle : {role.id}")
            embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
            embed.add_field(name="Date de création", value=f"<t:{int(time.time())}:F>", inline=False)

            config = load_config() 
            log_channel_id = config.get('log_channel') 
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")
            break

@bot.event
async def on_guild_role_delete(role):
    async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_delete):
        if entry.target.id == role.id:
            embed = discord.Embed(description=f"Le rôle `{role.name}` a été supprimé", color=discord.Color.red())
            embed.set_footer(text=f"ID du rôle : {role.id}")
            embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
            embed.add_field(name="Date de suppression", value=f"<t:{int(time.time())}:F>", inline=False)

            config = load_config() 
            log_channel_id = config.get('log_channel') 
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")
            break

@bot.event
async def on_guild_role_update(before, after):
    changes = []
    if before.name != after.name:
        changes.append(f"Nom : {before.name} → {after.name}")
    if before.color != after.color:
        changes.append(f"Couleur : {before.color} → {after.color}")
    if before.permissions != after.permissions:
        changes.append("Permissions modifiées")

    if changes:
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.role_update):
            if entry.target.id == after.id:
                embed = discord.Embed(description=f"Le rôle {after.mention} a été modifié", color=discord.Color.from_rgb(193, 168, 233))
                embed.set_footer(text=f"ID du rôle : {after.id}")
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.add_field(name="Changements", value="\n".join(changes), inline=False)
                embed.add_field(name="Date de modification", value=f"<t:{int(time.time())}:F>", inline=False)

                config = load_config() 
                log_channel_id = config.get('log_channel') 
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break

@bot.event
async def on_voice_state_update(member, before, after):
    
    if before.channel != after.channel:
        action = None
        if before.channel is None:
            action = "rejoint"
        elif after.channel is None:
            action = "quitté"
        else:
            action = "déplacé"

        if action == "déplacé":
            embed = discord.Embed(description=f"{member.mention} a été déplacé dans un autre salon vocal.", color=discord.Color.from_rgb(193,168,233))
            embed.set_footer(text=f"ID : {member.id}")
            embed.set_author(name=member.display_name, icon_url=member.avatar.url)
            embed.add_field(name="Salon vocal actuel", value=after.channel.jump_url if after.channel else "Aucun", inline=False)
            embed.add_field(name="Salon vocal précédent", value=before.channel.jump_url if before.channel else "Aucun", inline=False)
            embed.add_field(name="Date de modification", value=f"<t:{int(time.time())}:F>", inline=False)

            config = load_config() 
            log_channel_id = config.get('log_channel') 
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")
    
    if before.mute != after.mute or before.deaf != after.deaf:
        action = None
        if before.mute != after.mute and after.mute:
            action = "rendu muet"
        elif before.deaf != after.deaf and after.deaf:
            action = "mis en sourdine"
        elif before.mute != after.mute and not after.mute:
            action = "n'est plus muet"
        elif before.deaf != after.deaf and not after.deaf:
            action = "n'est plus en sourdine"

        if action:
            if before.channel is None:
                channel = after.channel
            else:
                channel = before.channel

            if before.channel and before.channel.guild.me.guild_permissions.view_audit_log:
                mod = None
                async for entry in before.channel.guild.audit_logs(action=discord.AuditLogAction.member_update):
                    if entry and entry.target.id == member.id and entry.user.id != bot.user.id:
                        mod = entry.user
                        break
            else:
                mod = None

            embed = discord.Embed(description=f"Le statut vocal de {member.mention} a été mis à jour.", color=discord.Color.from_rgb(193,168,233))
            if mod:
                embed.set_footer(text=f"{mod.display_name} | ID : {member.id}", icon_url=mod.avatar.url)
            else:
                embed.set_footer(text=f"ID : {member.id}")
            embed.set_author(name=member.display_name, icon_url=member.avatar.url)
            embed.add_field(name="Action", value=action, inline=True)
            embed.add_field(name="Muet", value="Oui" if after.mute else "Non", inline=True)
            embed.add_field(name="Sourd", value="Oui" if after.deaf else "Non", inline=True)
            embed.add_field(name="Salon vocal", value=channel.jump_url, inline=True)
            embed.add_field(name="Date de modification", value=f"<t:{int(time.time())}:F>", inline=False)

            config = load_config() 
            log_channel_id = config.get('log_channel') 
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")

@bot.event
async def on_scheduled_event_create(event):
    embed = discord.Embed(description=f"L'évenément `{event.name}` a été créé", color=discord.Color.green())
    embed.add_field(name="Description", value=event.description, inline=False)
    embed.add_field(name="Début", value=f"<t:{int(event.start_time.timestamp())}:F>" , inline=True)
    if event.end_time:
        embed.add_field(name="Fin", value=f"<t:{int(event.end_time.timestamp())}:F>", inline=True)
    if event.location:
        embed.add_field(name="Lieu", value=event.location, inline=False)
    if event.channel:
        embed.add_field(name="Salon", value=event.channel.jump_url, inline=False)
    embed.add_field(name="Date de création", value=f"<t:{int(time.time())}:F>", inline=False)
    if event.cover_image:
        embed.set_image(url=event.cover_image.url)
    
    creator = event.creator.display_name if event.creator else "Inconnu"
    creator_icon_url = event.creator.avatar.url if creator != "Inconnu" else discord.Embed.Empty
    embed.set_author(name=f"{creator}", icon_url=creator_icon_url)

    config = load_config() 
    log_channel_id = config.get('log_channel') 
    if log_channel_id:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(embed=embed)
        else:
            print("Le salon de logging n'existe pas.")
    else:
        print("Le salon de logging n'a pas été défini.")

@bot.event
async def on_scheduled_event_delete(event):
    embed = discord.Embed(description=f"L'évenément `{event.name}` a été déprogrammé", color=discord.Color.red())
    embed.add_field(name="Description", value=event.description, inline=False)
    embed.add_field(name="Début", value=f"<t:{int(event.start_time.timestamp())}:F>" , inline=True)
    if event.end_time:
        embed.add_field(name="Fin", value=f"<t:{int(event.end_time.timestamp())}:F>", inline=True)
    if event.location:
        embed.add_field(name="Lieu", value=event.location, inline=False)
    if event.channel:
        embed.add_field(name="Salon", value=event.channel.jump_url, inline=False)
    embed.add_field(name="Date de suppression", value=f"<t:{int(time.time())}:F>", inline=False)
    if event.cover_image:
        embed.set_image(url=event.cover_image.url)
    
    creator = event.creator.display_name if event.creator else "Inconnu"
    creator_icon_url = event.creator.avatar.url if creator != "Inconnu" else discord.Embed.Empty
    embed.set_author(name=f"{creator}", icon_url=creator_icon_url)

    config = load_config() 
    log_channel_id = config.get('log_channel') 
    if log_channel_id:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(embed=embed)
        else:
            print("Le salon de logging n'existe pas.")
    else:
        print("Le salon de logging n'a pas été défini.")

@bot.event
async def on_scheduled_event_update(before, after):
    changes = []
    if before.name != after.name:
        changes.append(f"Nom : {before.name} → {after.name}")
    if before.start_time != after.start_time:
        changes.append(f"Début : <t:{int(before.start_time.timestamp())}:F> → <t:{int(after.start_time.timestamp())}:F>"     )
    if before.end_time != after.end_time:
        changes.append(f"Fin : <t:{int(before.end_time.timestamp())}:F> → <t:{int(after.end_time.timestamp())}:F>"     )
    if before.description != after.description:
        changes.append(f"Description : {before.description} → {after.description}")
    if before.location != after.location:
        changes.append(f"Lieu : {before.location} → {after.location}")
    if before.cover_image != after.cover_image:
        changes.append("Image modifiée")
    if changes:
        embed = discord.Embed(description=f"L' événement `{after.name}` a été mis à jour", color=discord.Color.from_rgb(193, 168, 233))
        embed.set_footer(text=f"ID : {after.id}")
        
        updater_name = after.creator.display_name if after.creator else "Inconnu"
        updater_avatar_url = after.creator.avatar.url if updater_name != "Inconnu" else discord.Embed.Empty
        embed.set_author(name=f"{updater_name}", icon_url=updater_avatar_url)
        if after.cover_image:
            embed.set_image(url=after.cover_image.url)
        embed.add_field(name="Changements", value="\n".join(changes), inline=False)
        embed.add_field(name="Date de modification", value=f"<t:{int(time.time())}:F>", inline=False)

        config = load_config() 
        log_channel_id = config.get('log_channel') 
        if log_channel_id:
            log_channel = bot.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)
            else:
                print("Le salon de logging n'existe pas.")
        else:
            print("Le salon de logging n'a pas été défini.")

@bot.tree.command(name="say", description="Envoie un message personnalisé sur un salon textuel.")
@app_commands.describe(texte="Le message à envoyer", salon_textuel="Lien du salon textuel")
async def say(interaction: discord.Interaction, texte: str, salon_textuel: discord.TextChannel = None):
    if interaction.user.guild_permissions.administrator:
      if salon_textuel is not None:  
                await salon_textuel.send(texte)
                embed = discord.Embed(description=f"✅** Bravo!｜**" + "Message envoyé sur " + salon_textuel.jump_url , color=discord.Color.green())
                await interaction.response.send_message(embed=embed)
      else:
            erreur = "Le salon textuel n'existe pas."
            embed = discord.Embed(description=f"❌** Erreur｜**" + f"{erreur}" , color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
            erreur = "Vous n'avez pas les permissions requises pour éxécuter cette commande."
            embed = discord.Embed(description=f"❌** Erreur｜**" + f"{erreur}" , color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)               

@bot.tree.command(name="avatar",description="Affiche l'avatar d'un utilisateur.")
@app_commands.describe(utilisateur="L'utilisateur dont vous voulez connaitre l'avatar")
async def avatar(interaction: discord.Interaction,  utilisateur: discord.Member ):
    embed = discord.Embed(title=f"Avatar de {utilisateur.display_name}",  color=discord.Color.from_rgb(193,168,233) )
    embed.set_image(url=utilisateur.avatar)
    
    download_link = f"[Lien de l'image]({utilisateur.avatar})"
    embed.add_field(name="", value=download_link)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="profileavatar",description="Affiche l'avatar de profil d'un utilisateur.")
@app_commands.describe(utilisateur="L'utilisateur dont vous voulez connaitre l'avatar")
async def profileavatar(interaction: discord.Interaction,  utilisateur: discord.Member ):
    embed = discord.Embed(title=f"Avatar de {utilisateur.display_name}",  color=discord.Color.from_rgb(193,168,233) )
    embed.set_image(url=utilisateur.display_avatar)
    
    download_link = f"[Lien de l'image]({utilisateur.display_avatar})"
    embed.add_field(name="", value=download_link)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="servericon",description="Affiche l'icône du serveur actuel.")
async def servericon(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    guild = bot.get_guild(guild_id)
    embed = discord.Embed(title=f"Icône du serveur {guild}",  color=discord.Color.from_rgb(193,168,233) )
    embed.set_image(url=guild.icon.url)
    download_link = f"[Lien de l'image]({guild.icon})"
    embed.add_field(name="", value=download_link)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help",description="Affiche des informations concernant [uv]bot.")
async def help(interaction: discord.Interaction):
 
    embed = discord.Embed(title="[uv]bot", description="[uv]bot est un bot discord crée exclusivement pour le serveur ultraviolet et présente de nombreuses fonctionnalitées essentielles.", color=discord.Color.from_rgb(193,168,233))
    embed.add_field(name=f"Version", value=f"{version}", inline=True)
    view = discord.ui.View() 
    style = discord.ButtonStyle.grey 
    item = discord.ui.Button(style=style, label="Github", url="https://github.com/dxnuv/uv-bot")  
    view.add_item(item=item)
    await interaction.response.send_message(embed=embed,view=view)

@bot.tree.command(name="loveletter",description="Dévoile l'amour que tu portes envers une personne de ce serveur.")
@app_commands.describe(utilisateur="L'utilisateur dont vous voulez connaitre l'avatar", message="Le message que vous voulez envoyer à votre cutie lover", anonyme="Afichage (ou non) de votre pseudo")
async def loveletter(interaction: discord.Interaction, utilisateur: discord.Member , message: str, anonyme: bool = False):
    guild_id = interaction.guild_id
    guild = bot.get_guild(guild_id)
    
    embed = discord.Embed(title=f"💌 Un membre du serveur {guild} vous a envoyé une lettre d'amour...", color=discord.Color.from_rgb(242, 80, 83))
    embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Cher,", value=utilisateur.mention, inline=False)
    embed.add_field(name="Message :", value=message, inline=False)
    if anonyme:
        embed.add_field(name="Signé, ", value="pookie bear anonyme 🥰")
    else:
        embed.add_field(name="Signé, ", value=interaction.user.mention + " 🥰")
        await utilisateur.send(embed=embed)
        embed = discord.Embed(description=f"✅** Bravo!｜**" + "💌 Lettre d'amour envoyé à " + utilisateur.mention , color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
@bot.tree.command(name="archive", description="Archive un salon textuel.")
@app_commands.describe(salon_textuel="Lien du salon textuel")
async def archive(interaction: discord.Interaction, salon_textuel: discord.TextChannel):

    if interaction.user.guild_permissions.administrator:
         date_formattee = datetime.now().strftime("%d-%m-%y")
         nom_salon_archives = f"{salon_textuel.name}-{date_formattee}"  
         categorie_archives = discord.utils.get(interaction.guild.categories, name="📦 archives")

         if categorie_archives is None:
             erreur = "La catégorie '📦 archives' n'a pas été trouvée."
             embed = discord.Embed(description=f"❌** Erreur｜**" + f"{erreur}" , color=discord.Color.red())
             await interaction.response.send_message(embed=embed, ephemeral=True)
         else:
             await salon_textuel.edit(category=categorie_archives)

             salon_textuel_og = salon_textuel.name
             await salon_textuel.edit(name=nom_salon_archives)

             await salon_textuel.edit(position=0)

             embed = discord.Embed(description=f"✅** Bravo!｜**" + f"Le salon textuel `{salon_textuel_og}` a été archivé avec succès." , color=discord.Color.green())
             await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
            erreur = "Vous n'avez pas les permissions requises pour éxécuter cette commande."
            embed = discord.Embed(description=f"❌** Erreur｜**" + f"{erreur}" , color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
   
@bot.tree.command(name="lock",description="Désactive un salon textuel.")
@app_commands.describe(salon_textuel="Le salon que vous souhaitez désactiver")
async def lock(interaction: discord.Interaction, salon_textuel: discord.TextChannel = None):
     if interaction.user.guild_permissions.administrator:
          if salon_textuel is None:
                await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
                embed = discord.Embed(description=f"✅** Bravo!｜**" + f"Le salon textuel {interaction.channel.jump_url} a été désactivé avec succès." , color=discord.Color.green())
                await interaction.response.send_message(embed=embed)
          else:
               await salon_textuel.set_permissions(interaction.guild.default_role, send_messages=False)
               embed = discord.Embed(description=f"✅** Bravo!｜**" + f"Le salon textuel {salon_textuel.jump_url} a été désactivé avec succès." , color=discord.Color.green())
               await interaction.response.send_message(embed=embed)


     else:
             erreur = "Vous n'avez pas les permissions requises pour éxécuter cette commande."
             embed = discord.Embed(description=f"❌** Erreur｜**" + f"{erreur}" , color=discord.Color.red())
             await interaction.response.send_message(embed=embed, ephemeral=True)    

@bot.tree.command(name="unlock",description="Réactive un salon textuel désactivé.")
@app_commands.describe(salon_textuel="Le salon que vous souhaitez réactiver")
async def unlock(interaction: discord.Interaction, salon_textuel: discord.TextChannel = None):
     if interaction.user.guild_permissions.administrator:
          if salon_textuel is None:
                await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
                embed = discord.Embed(description=f"✅** Bravo!｜**" + f"Le salon textuel {interaction.channel.jump_url} a été réactivé avec succès." , color=discord.Color.green())
                await interaction.response.send_message(embed=embed)
          else:
               await salon_textuel.set_permissions(interaction.guild.default_role, send_messages=True)
               embed = discord.Embed(description=f"✅** Bravo!｜**" + f"Le salon textuel {salon_textuel.jump_url} a été réactivé avec succès." , color=discord.Color.green())
               await interaction.response.send_message(embed=embed)


     else:
             erreur = "Vous n'avez pas les permissions requises pour éxécuter cette commande."
             embed = discord.Embed(description=f"❌** Erreur｜**" + f"{erreur}" , color=discord.Color.red())
             await interaction.response.send_message(embed=embed, ephemeral=True)    

@bot.tree.command(name="rename", description="Renomme un salon textuel.")
@app_commands.describe(salon_textuel="Lien du salon textuel", nouveau_nom="Nouveau nom du salon textuel")
async def rename(interaction: discord.Interaction, salon_textuel: discord.TextChannel, nouveau_nom: str):
    if interaction.user.guild_permissions.administrator:
        try:
            nom_actuel = salon_textuel.name
            if '｜' in nom_actuel: 
                nom_actuel = nom_actuel.split('｜', 1)[-1]
                nouveau_nom_complet = f"{salon_textuel.name.split('｜', 1)[0]}｜{nouveau_nom}"
            else:
                nouveau_nom_complet = nouveau_nom
            await salon_textuel.edit(name=nouveau_nom_complet)
            embed = discord.Embed(description=f"✅** Bravo!｜** Le salon textuel `{nom_actuel}` a été renommé en `{nouveau_nom_complet}` avec succès.", color=discord.Color.green())
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            erreur = f"Une erreur s'est produite lors du renommage du salon textuel : {e}"
            embed = discord.Embed(description=f"❌** Erreur｜** {erreur}", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
    else:
        erreur = "Vous n'avez pas les permissions requises pour exécuter cette commande."
        embed = discord.Embed(description=f"❌** Erreur｜** {erreur}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

def load_tags():
    try:
        with open('tags.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Le fichier tags.json n'a pas été trouvé.")
        return {}
    except Exception as e:
        print(f"Une erreur s'est produite lors de la lecture du fichier tags.json : {e}")
        return {}

def save_tags(tags):
    with open('tags.json', 'w') as file:
        json.dump(tags, file, indent=4)

tag_group = app_commands.Group(name="tag", description="Commandes liés aux tags")

@tag_group.command(name="use", description="Utilise un tag enregistré.")
@app_commands.describe(tag_nom="Nom du tag")
async def use_tag(interaction: discord.Interaction, tag_nom: str):
    tags = load_tags()
    if tag_nom in tags:
        tag_data = tags[tag_nom]
        if tag_data["private"]:
            user_id = str(interaction.user.id)
            if user_id != tag_data["creator_id"]:
                embed = discord.Embed(description="❌ **Erreur｜** Vous n'êtes pas autorisé à utiliser ce tag privé.", color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)  
                return
        texte = tag_data["texte"]
        await interaction.response.send_message(texte, ephemeral=tag_data["private"])  
    else:
        embed = discord.Embed(description="❌ **Erreur｜** Ce tag n'existe pas.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)  

@tag_group.command(name="new", description="Crée un nouveau tag.")
@app_commands.describe(tag_nom="Nom du tag", texte="Texte intégré au tag", privé="Tag accessible par tous (ou non)")
async def create_tag(interaction: discord.Interaction, tag_nom: str, texte: str, privé: bool = False):
    tags = load_tags()
    user_id = str(interaction.user.id)
    if tag_nom in tags:
        embed = discord.Embed(description=f"❌ **Erreur｜** Le tag `{tag_nom}` existe déjà.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    tags[tag_nom] = {"texte": texte, "creator_id": user_id, "private": privé}
    save_tags(tags)
    embed = discord.Embed(description=f"✅ **Bravo!｜** Le tag `{tag_nom}` a été créé avec succès !", color=discord.Color.green())
    await interaction.response.send_message(embed=embed)

@tag_group.command(name="remove", description="Supprime un tag créé par vous.")
@app_commands.describe(tag_nom="Nom du tag")
async def remove_tag(interaction: discord.Interaction, tag_nom: str):
    tags = load_tags()
    user_id = str(interaction.user.id)
    
    if tag_nom not in tags:
        embed = discord.Embed(description="❌ **Erreur｜** Ce tag n'existe pas.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    if tags[tag_nom]["creator_id"] == user_id or interaction.user.guild_permissions.administrator:
        del tags[tag_nom]
        save_tags(tags)
        embed = discord.Embed(description=f"✅ **Bravo!｜** Le tag `{tag_nom}` a été supprimé avec succès !", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(description="❌ **Erreur｜** Vous n'êtes pas l'auteur de ce tag ou vous n'avez pas les permissions requises.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

@tag_group.command(name="list", description="Affiche l'ensemble des tags.")
async def tag_list(interaction: discord.Interaction):
    tags = load_tags()
    if not tags:
        embed = discord.Embed(title="Liste des tags", description="Aucun tag n'a été créé 😔. Utilisez `/tag new` pour créer un nouveau tag.", color=discord.Color.from_rgb(193,168,233 ))
        await interaction.response.send_message(embed=embed)
        return
    sorted_tags = sorted(tags.items()) 
    pages = []
    page_content = ""
    tags_per_page = 5
    current_page = 1
    total_pages = (len(sorted_tags) - 1) // tags_per_page + 1 
    for index, (tag_nom, data) in enumerate(sorted_tags, start=1):
        creator = interaction.guild.get_member(int(data["creator_id"]))
        if creator:
            creator_name = creator.display_name
        else:
            creator_name = "Utilisateur Inconnu"
        if data["private"]:
            lock_icon = f"`🔒 Privé ` "
        else:
            lock_icon = f"`🔓 Publique ` "
        page_content += f"**{tag_nom}**  {lock_icon}\n`Auteur` : {creator_name}\n\n"
        if index % tags_per_page == 0 or index == len(sorted_tags):
            pages.append(discord.Embed(title=f"Liste des tags ({current_page}/{total_pages})", description=page_content , color=discord.Color.from_rgb(193,168,233 ), ))
            page_content = ""
            current_page += 1
    
    paginator = Paginator.Simple()
    await paginator.start(interaction, pages=pages)

@bot.tree.command(name="customemoji", description="Affiche l'image d'un emoji personnalisé.")
@app_commands.describe(emoji_nom="Nom de l'emoji personnalisé")
async def custom_emoji(interaction: discord.Interaction, emoji_nom: str):
    emoji = discord.utils.get(interaction.guild.emojis, name=emoji_nom)
    if emoji is None:
        embed = discord.Embed(description=f"❌ **Erreur｜** L'emoji personnalisé `{emoji_nom}` n'a pas été trouvé.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    emoji_url = emoji.url

    embed = discord.Embed(title=f"Emoji personnalisé : `{emoji_nom}`", color=discord.Color.from_rgb(193, 168, 233))
    embed.set_image(url=emoji_url)
    download_link = f"[Lien de l'image]({emoji_url})"
    embed.add_field(name="", value=download_link)
    await interaction.response.send_message(embed=embed)

bot.tree.add_command(tag_group)

def change_profile_picture(token, image_path):
    try:
        image_path = image_path.replace('"',"")
        image_path = image_path.replace("'","")
        image_path = image_path.strip()
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        headers = {
            "Authorization": f"Bot {token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "Content-Type": "application/json"
        }
        data = {
            "avatar": f"data:image/png;base64,{encoded_image}"
        }
        url = "https://discord.com/api/v9/users/@me"
        response = requests.patch(url, headers=headers, json=data)
        if response.status_code != 200:
            print(f"An error occurred: {response.json()}")
            return

        print('Profile picture has been changed succesfully.')
    except Exception as e:
        print(f"An error occurred: {e}")


def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Le fichier config.json n'a pas été trouvé.")
        return {}
    except Exception as e:
        print(f"Une erreur s'est produite lors de la lecture du fichier config.json : {e}")
        return {}

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

log_group = app_commands.Group(name="log", description="Commandes liés aux logs")
bot.tree.add_command(log_group)

@log_group.command(name="set", description="Définit un salon de logging.")
@app_commands.describe(salon_textuel="Lien du salon choisi.")
async def set_log_channel(interaction: discord.Interaction, salon_textuel: discord.TextChannel):

    log_channel = salon_textuel.id
    config = load_config()
    config['log_channel'] = log_channel
    save_config(config)
    embed = discord.Embed(description=f"✅** Bravo!｜**" + f"Le salon textuel {salon_textuel.jump_url} a été défini comme salon de logging avec succès." , color=discord.Color.green())
    await interaction.response.send_message(embed=embed)

config = load_config()
token = config['token']

image_path = "images\icon_uv-gifpp.gif"
print("Profile picture found.")
change_profile_picture(token, image_path)
bot.run(token)