import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context

from otter_welcome_buddy.common.handlers.leetcode import LeetcodeAPI
from otter_welcome_buddy.common.utils.discord_ import send_message
from otter_welcome_buddy.common.utils.types.handlers import UserPublicProfileType
from otter_welcome_buddy.database.db_user import DbUser
from otter_welcome_buddy.database.db_leetcode_user import DbLeetcodeUser
from otter_welcome_buddy.database.dbconn import session_scope
from otter_welcome_buddy.database.models.leetcode_model import LeetcodeUserModel
from otter_welcome_buddy.database.models.user_model import UserModel


_LEETCODE_BASE_URL = "https://leetcode.com/"
_USERNAME_REGISTER_WAIT_TIME = 60
_USERNAME_REGISTER_COUNTRY = "Zimbabwe"


class LeetcodeChallenge(commands.Cog):
    """
    Leetcode Challenge command events, activity to run a tourney and won the user with most points at the end
    Commands:
        lchallenge register:                                User register their leetcode account
        lchallenge unregister:                              Removes the leetcode account associated to an user
        lchallenge start <start_timestamp> [end_timestamp]: Start the challenge at certain time (or now) and
                                                            runs to certain time (or 7 days by default)
        lchallenge end:                                     Finish the challenge immediately
    """

    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.leetcode_client = LeetcodeAPI()

    @commands.group(
        brief="Commands related to Leetcode challenge!",
        invoke_without_command=True,
        pass_context=True,
    )
    async def lchallenge(self, ctx: Context) -> None:
        """
        Leetcode Challenge will run a tournament for certain time and is won by the user with most points
        """
        await ctx.send_help(ctx.command)
    
    async def _verify_leetcode_username(self, ctx: Context, username: str) -> UserPublicProfileType | None:
        leetcode_user: UserPublicProfileType | None = self.leetcode_client.get_user_public_profile(username)
        if leetcode_user is None:
            await ctx.send(
                f"The username {username} doesn't appears on Leetcode, are you certain about your existence?"
            )
            return None

        await send_message(
            ctx,
            f"Please change your **Location** on [this link]({_LEETCODE_BASE_URL}profile/) to "
            f"`{_USERNAME_REGISTER_COUNTRY}` within {_USERNAME_REGISTER_WAIT_TIME} seconds {ctx.author.mention}.\n",
        )
        await asyncio.sleep(_USERNAME_REGISTER_WAIT_TIME)

        leetcode_user = self.leetcode_client.get_user_public_profile(username)
        if leetcode_user is None or leetcode_user.profile.countryName != _USERNAME_REGISTER_COUNTRY:
            await ctx.send(f"Unable to set your username, please try again {ctx.author.mention}")
            return None

        return leetcode_user

    @lchallenge.command(brief="Register your leetcode account", usage="[handle]")  # type: ignore
    async def register(self, ctx: Context, username: str) -> None:
        """Link a leetcode account to discord account by changing your country in the profile"""
        with session_scope() as session:
            user_model: UserModel | None = DbUser.get_user(user_id=ctx.author.id, session=session)
            # If the user is not found, we'll insert the user to the database as well
            if user_model is None:
                user_model = UserModel(
                    discord_id=ctx.author.id,
                )
            
            # If there's any username set, we should flag either if is the same or different
            if user_model.leetcode_handle is not None:
                if user_model.leetcode_handle != username:
                    await ctx.send("You have a different username setup, remove it first before setting up again")
                else:
                    await ctx.send("You already registered that username, don't you remember?")
                return
            
            user_check_model: UserModel | None = DbUser.get_user_by_handle(handle=username, session=session)
            if user_check_model is not None:
                await ctx.send("The username is currently associated to a different user, please verify")
                return

            leetcode_user: UserPublicProfileType | None = await self._verify_leetcode_username(
                ctx=ctx, 
                username=username,
            )
            if leetcode_user is None: 
                return
            
            leetcode_user_model: LeetcodeUserModel = LeetcodeUserModel(
                handle=username,
                rating=leetcode_user.profile.ranking,
                user_avatar=leetcode_user.profile.userAvatar,
            )
            user_model.leetcode_handle = username
            user_model.leetcode_user = leetcode_user_model
            DbLeetcodeUser.insert_leetcode_user(
                leetcode_user_model=leetcode_user_model, 
                session=session, 
                override=True,
            )
            DbUser.insert_user(user_model=user_model, session=session, override=True)

            embed = discord.Embed(
                description=f"Username for {ctx.author.mention} successfully set "
                f"to [{username}]({_LEETCODE_BASE_URL}{username})."
                f"Feel free to erase the Location (unless you enjoyed being part of {_USERNAME_REGISTER_COUNTRY})",
                color=discord.Color.teal(),
            )
            embed.add_field(name="Ranking", value=str(leetcode_user.profile.ranking), inline=True)
            embed.set_thumbnail(url=leetcode_user.profile.userAvatar)
            await ctx.send(embed=embed)

    @lchallenge.command(brief="Remove your leetcode account")  # type: ignore
    async def unregister(self, ctx: Context) -> None:
        """Remove the leetcode account associated with the user"""
        with session_scope() as session:
            user_model: UserModel | None = DbUser.get_user(
                user_id=ctx.author.id,
                session=session,
            )
            msg: str = ""
            if user_model is not None and user_model.leetcode_handle is not None:
                user_model.leetcode_handle = None
                user_model.leetcode_user = None
                DbUser.insert_user(user_model=user_model, session=session, override=True)
                msg = "Leetcode username removed! 🥳"
            else:
                msg = "To remove something first you need to add it. 🤨"
            await ctx.send(msg)


async def setup(bot: Bot) -> None:
    """Required setup method"""
    await bot.add_cog(LeetcodeChallenge(bot))
