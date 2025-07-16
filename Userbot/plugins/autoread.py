from Userbot import nlx
from Userbot.helper.database import dB
from Userbot.helper.tools import Emojik, h_s, initial_ctext, zb

__MODULES__ = "AutoRead"
USER_PREMIUM = True


def help_string(org):
    return h_s(org, "help_autoread")


@zb.ubot("autoread|autor")
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    mek = await m.reply(_("proses").format(em.proses, proses_))
    if len(m.command) < 3:
        await mek.edit(_("autoread_1").format(em.gagal))
        return
    biji, peler, jembut = m.command[:3]
    if peler.lower() == "time":
        if jembut.isnumeric():
            lmt = int(jembut)
            dB.set_var(c.me.id, "time_read", lmt)
            await mek.edit(
                "<b>{} Waktu Autoread diatur ke : `{}`</b>".format(em.sukses, lmt)
            )
            return
        else:
            await mek.edit(
                "<b>Kasih angkalah tolol!! Goblok banget udah tau ini waktu berupa angka malah kasih huruf. Idiot!!</b>".format(
                    em.gagal
                )
            )
            return
    elif peler.lower() == "gc":
        if jembut.lower() == "on":
            dB.set_var(c.me.id, "read_gc", True)
            await mek.edit(_("autoread_2").format(em.sukses))
            return
        else:
            dB.remove_var(c.me.id, "read_gc")
            await mek.edit(_("autoread_8").format(em.sukses, peler))
            return
    elif peler.lower() == "us":
        if jembut.lower() == "on":
            dB.set_var(c.me.id, "read_us", True)
            await mek.edit(_("autoread_3").format(em.sukses))
            return
        else:
            dB.remove_var(c.me.id, "read_us")
            await mek.edit(_("autoread_8").format(em.sukses, peler))
            return
    elif peler.lower() == "bot":
        if jembut.lower() == "on":
            dB.set_var(c.me.id, "read_bot", True)
            await mek.edit(_("autoread_7").format(em.sukses))
            return
        else:
            dB.remove_var(c.me.id, "read_bot")
            await mek.edit(_("autoread_8").format(em.sukses, peler))
            return
    elif peler.lower() == "ch":
        if jembut.lower() == "on":
            dB.set_var(c.me.id, "read_ch", True)
            await mek.edit(_("autoread_4").format(em.sukses))
            return
        else:
            dB.remove_var(c.me.id, "read_ch")
            await mek.edit(_("autoread_8").format(em.sukses, peler))
            return

    elif peler.lower() == "tag":
        if jembut.lower() == "on":
            dB.set_var(c.me.id, "read_mention", True)
            await mek.edit(_("autoread_9").format(em.sukses))
            return
        else:
            dB.remove_var(c.me.id, "read_mention")
            await mek.edit(_("autoread_8").format(em.sukses, peler))
            return

    elif peler.lower() == "all":
        if jembut.lower() == "on":
            dB.set_var(c.me.id, "read_all", True)
            await mek.edit(_("autoread_5").format(em.sukses))
            return
        else:
            dB.remove_var(c.me.id, "read_all")
            await mek.edit(_("autoread_8").format(em.sukses, peler))
            return
    else:
        await mek.edit(_("autoread_6").format(em.gagal))
        return
