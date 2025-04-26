#  Author: Aaron Fulton
#  Date: 2025-04-26
#  Description: Script to export data from a Discord server
#  License: GNU General Public License v3.0

import os
import csv
import sys
import asyncio
import discord
import logging
import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s[%(levelname)s]%(reset)s %(message)s",
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    }
))
logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

GUILD_ID = 1319879625148596264
ROLE_ID = 1320810862012928020
CLOSED_STATUS_ROLE_ID = 1331653077974913168

SERVICE_ROLE_TO_FORUM_CHANNEL = {
    "Artist": (1320810708312653974, 1321806727271809064),
    "Animator": (1320810733759631431, 1321807652627677236),
    "Textures": (1355763130776686732, 1321806866270912542),
    "Developer": (1320810670001750026, 1321807024337715210),
    "Editor": (1320810835970359418, 1321807415297179682),
    "Logos": (1355763408049275041, 1321807261290463273),
    "Skins": (1322967028730167436, 1321806901125713991),
    "Thumbnails": (1349191393377128488, 1321806796142149632),
    "Music": (1355739928423825578, 1355739828657979630),
    "Builder": (1322967179800477899, 1322303664878129234),
    "Mythic Mobs": (1351173128386248704, 1351170019127590922),
}

class ExportClient(discord.Client):
    def __init__(self, output_dir, **kwargs):
        super().__init__(**kwargs)
        self.output_dir = output_dir

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")

        guild = self.get_guild(GUILD_ID)
        if not guild:
            logger.error("Guild not found.")
            await self.close()
            return

        role = guild.get_role(ROLE_ID)
        if not role:
            logger.error("Role not found.")
            await self.close()
            return

        logger.info("Fetching all members...")
        all_members = [member async for member in guild.fetch_members(limit=None)]

        logger.info("Fetching forum channels and threads...")
        forum_channels_by_service = {
            service_name: guild.get_channel(forum_channel_id)
            for service_name, (_, forum_channel_id) in SERVICE_ROLE_TO_FORUM_CHANNEL.items()
        }

        threads_by_service = {}
        for service_name, forum_channel in forum_channels_by_service.items():
            if not forum_channel:
                logger.warning(f"Forum channel for '{service_name}' not found.")
                continue

            all_threads = list(forum_channel.threads)
            async for archived_thread in forum_channel.archived_threads(limit=None):
                all_threads.append(archived_thread)

            threads_by_service[service_name] = all_threads

        logger.info("Processing members...")
        csv_rows = []
        for member in all_members:
            if role not in member.roles:
                continue

            member_service_roles = [
                role for role in member.roles
                if role.id in (service_role_id for service_role_id, _ in SERVICE_ROLE_TO_FORUM_CHANNEL.values())
            ]
            has_closed_status = any(role.id == CLOSED_STATUS_ROLE_ID for role in member.roles)

            service_submission_status = {}
            for service_name, (service_role_id, _) in SERVICE_ROLE_TO_FORUM_CHANNEL.items():
                if any(role.id == service_role_id for role in member_service_roles):
                    member_threads = threads_by_service.get(service_name, [])
                    has_post_in_forum = any(thread.owner_id == member.id for thread in member_threads)
                    service_submission_status[service_name] = has_post_in_forum

            csv_rows.append({
                "Username": member.name,
                "DiscordUserID": member.id,
                "AssignedServices": "; ".join(role.name for role in member_service_roles),
                "IsClosed": has_closed_status,
                **service_submission_status,
            })

        fieldnames = ["Username", "DiscordUserID", "AssignedServices", "IsClosed"] + list(SERVICE_ROLE_TO_FORUM_CHANNEL.keys())
        csv_path = os.path.join(self.output_dir, "freelancer.csv")

        logger.info(f"Saving CSV to {csv_path}...")
        with open(csv_path, mode="w", newline="", encoding="utf-8") as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(csv_rows)

        logger.info("CSV export completed successfully.")
        await self.close()


async def run_export(discord_token, output_dir):
    intents = discord.Intents.default()
    intents.members = True
    intents.guilds = True
    intents.message_content = True

    client = ExportClient(output_dir, intents=intents)
    try:
        await client.start(discord_token)
    finally:
        await client.close() 
def main():
    if len(sys.argv) < 3:
        logger.error("Usage: freelancer_export_script <token> <output_directory>")
        sys.exit(1)

    discord_token = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(output_dir):
        logger.info(f"Creating output directory at {output_dir}...")
        os.makedirs(output_dir)

    asyncio.run(run_export(discord_token, output_dir))
    return 0

if __name__ == "__main__":
    sys.exit(main())
