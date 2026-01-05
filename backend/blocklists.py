"""
Blocklists for email validation.
Contains lists of disposable email domains, role-based prefixes, and free email providers.
"""

# Disposable/temporary email domains (commonly used for spam or throwaway accounts)
# This is a curated list of the most common ones
DISPOSABLE_DOMAINS = {
    # Popular temporary email services
    "mailinator.com", "guerrillamail.com", "guerrillamail.org", "guerrillamail.net",
    "tempmail.com", "temp-mail.org", "tempmail.net", "tempail.com",
    "10minutemail.com", "10minutemail.net", "10minemail.com",
    "yopmail.com", "yopmail.fr", "yopmail.net",
    "throwaway.email", "throwawaymail.com", "throam.com",
    "trashmail.com", "trashmail.net", "trashmail.org", "trash-mail.com",
    "fakeinbox.com", "fakemailgenerator.com", "fakemail.net",
    "getnada.com", "nada.email", "getairmail.com",
    "mohmal.com", "mohmal.im", "mohmal.tech",
    "dispostable.com", "disposeamail.com", "disposableemailaddresses.com",
    "mailnesia.com", "mailnator.com", "mailinater.com",
    "sharklasers.com", "spam4.me", "spamgourmet.com",
    "maildrop.cc", "mailsac.com", "mailcatch.com",
    "burnermail.io", "burner.kiwi", "burnmail.com",
    "33mail.com", "spamex.com", "spamfree24.org",
    "mytrashmail.com", "mt2014.com", "mt2015.com",
    "mintemail.com", "mintmail.com", "tempmailaddress.com",
    "mailforspam.com", "emailondeck.com", "tempr.email",
    "discard.email", "discardmail.com", "discardmail.de",
    "spamherelots.com", "spamhereplease.com", "spambox.us",
    "incognitomail.org", "incognitomail.com", "anonymbox.com",
    "crazymailing.com", "deadaddress.com", "despam.it",
    "devnullmail.com", "dontsendmespam.de", "dump-email.info",
    "dumpmail.de", "emailigo.de", "emailtemporanea.net",
    "emz.net", "ephemail.net", "etranquil.com",
    "evopo.com", "fastacura.com", "filzmail.com",
    "fizmail.com", "flyspam.com", "frapmail.com",
    "getonemail.com", "gishpuppy.com", "goemailgo.com",
    "haltospam.com", "hidemail.de", "hochsitze.com",
    "hulapla.de", "ichimail.com", "imails.info",
    "inboxalias.com", "inboxclean.com", "inboxclean.org",
    "jetable.com", "jetable.fr.nf", "jetable.net",
    "jetable.org", "kasmail.com", "kaspop.com",
    "keepmymail.com", "killmail.com", "killmail.net",
    "klassmaster.com", "klassmaster.net", "klzlv.com",
    "kulturbetrieb.info", "kurzepost.de", "letthemeatspam.com",
    "lhsdv.com", "lifebyfood.com", "link2mail.net",
    "litedrop.com", "lol.ovpn.to", "lookugly.com",
    "lopl.co.cc", "lortemail.dk", "lovemeleaveme.com",
    "lr78.com", "maboard.com", "mail-hierarchie.net",
    "mail-temporaire.fr", "mail.by", "mail.mezimages.net",
    "mail2rss.org", "mailbidon.com", "mailblocks.com",
    "mailcatch.com", "mailde.de", "mailde.info",
    "maildx.com", "mailed.ro", "mailexpire.com",
    "mailfa.tk", "mailfork.com", "mailfreeonline.com",
    "mailguard.me", "mailin8r.com", "mailinater.com",
    "mailinator.net", "mailinator.org", "mailinator.us",
    "mailinator2.com", "mailincubator.com", "mailismagic.com",
    "mailjunk.cf", "mailjunk.ga", "mailjunk.gq",
    "mailjunk.ml", "mailjunk.tk", "mailmate.com",
    "mailme.gq", "mailme.ir", "mailme.lv",
    "mailmetrash.com", "mailmoat.com", "mailnull.com",
    "mailorg.org", "mailpick.biz", "mailproxsy.com",
    "mailquack.com", "mailrock.biz", "mailscrap.com",
    "mailshell.com", "mailsiphon.com", "mailslapping.com",
    "mailslite.com", "mailspam.xyz", "mailsyphon.com",
    "mailtemp.info", "mailtome.de", "mailtothis.com",
    "mailzilla.com", "mailzilla.org", "mbx.cc",
    "mega.zik.dj", "meinspamschutz.de", "meltmail.com",
    "messagebeamer.de", "mierdamail.com", "ministry-of-silly-walks.de",
    "mintemail.com", "misterpinball.de", "moncourrier.fr.nf",
    "monemail.fr.nf", "monmail.fr.nf", "monumentmail.com",
    "ms9.mailslite.com", "msa.minsmail.com", "msb.minsmail.com",
    "mxfuel.com", "mypartyclip.de", "myphantomemail.com",
    "myspaceinc.com", "myspaceinc.net", "myspacepimpedup.com",
    "mytempemail.com", "mytempmail.com", "mytrashmail.com",
    "neomailbox.com", "nervmich.net", "nervtmansen.de",
    "netmails.com", "netmails.net", "netzidiot.de",
    "neverbox.com", "no-spam.ws", "nobulk.com",
    "noclickemail.com", "nogmailspam.info", "nomail.xl.cx",
    "nomail2me.com", "nomorespamemails.com", "nospam.ze.tc",
    "nospam4.us", "nospamfor.us", "nospammail.net",
    "nospamthanks.info", "notmailinator.com", "nowhere.org",
    "nowmymail.com", "nurfuerspam.de", "nus.edu.sg",
    "nwldx.com", "objectmail.com", "obobbo.com",
    "odnorazovoe.ru", "ohaaa.de", "oneoffemail.com",
    "onewaymail.com", "online.ms", "oopi.org",
    "opayq.com", "ordinaryamerican.net", "otherinbox.com",
    "ourklips.com", "outlawspam.com", "ovpn.to",
    "owlpic.com", "pancakemail.com", "pjjkp.com",
    "plexolan.de", "poczta.onet.pl", "politikerclub.de",
    "poofy.org", "pookmail.com", "privacy.net",
    "privy-mail.com", "privymail.de", "proxymail.eu",
    "prtnx.com", "punkass.com", "putthisinyourspamdatabase.com",
    "qq.com", "quickinbox.com", "quickmail.nl",
    "rcpt.at", "reallymymail.com", "realtyalerts.ca",
    "recode.me", "reconmail.com", "recursor.net",
    "recyclemail.dk", "regbypass.com", "regbypass.comsafe-mail.net",
    "rejectmail.com", "reliable-mail.com", "remail.cf",
    "remail.ga", "rhyta.com", "rklips.com",
    "rmqkr.net", "rppkn.com", "rtrtr.com",
    "s0ny.net", "safe-mail.net", "safersignup.de",
    "safetymail.info", "safetypost.de", "sandelf.de",
    "saynotospams.com", "schafmail.de", "schrott-email.de",
    "secretemail.de", "secure-mail.biz", "selfdestructingmail.com",
    "sendspamhere.com", "sharedmailbox.org", "sharklasers.com",
    "shieldemail.com", "shiftmail.com", "shitmail.me",
    "shortmail.net", "shut.name", "shut.ws",
    "sibmail.com", "sinnlos-mail.de", "siteposter.net",
    "skeefmail.com", "slaskpost.se", "slopsbox.com",
    "slowfoodfoothills.xyz", "smashmail.de", "smellfear.com",
    "snakemail.com", "sneakemail.com", "snkmail.com",
    "sofimail.com", "sofort-mail.de", "softpls.asia",
    "sogetthis.com", "soisz.com", "solvemail.info",
    "soodonims.com", "spam.la", "spam.su",
    "spam4.me", "spamavert.com", "spambob.com",
    "spambob.net", "spambob.org", "spambog.com",
    "spambog.de", "spambog.net", "spambog.ru",
    "spambox.info", "spambox.irishspringrealty.com", "spambox.us",
    "spamcannon.com", "spamcannon.net", "spamcero.com",
    "spamcon.org", "spamcorptastic.com", "spamcowboy.com",
    "spamcowboy.net", "spamcowboy.org", "spamday.com",
    "spameater.com", "spameater.org", "spamex.com",
    "spamfree.eu", "spamfree24.com", "spamfree24.de",
    "spamfree24.eu", "spamfree24.info", "spamfree24.net",
    "spamgoes.in", "spamgourmet.com", "spamgourmet.net",
    "spamgourmet.org", "spamherelots.com", "spamhereplease.com",
    "spamhole.com", "spamify.com", "spaminator.de",
    "spamkill.info", "spaml.com", "spaml.de",
    "spammotel.com", "spamobox.com", "spamoff.de",
    "spamsalad.in", "spamslicer.com", "spamspot.com",
    "spamstack.net", "spamthis.co.uk", "spamthisplease.com",
    "spamtrail.com", "spamtroll.net", "speed.1s.fr",
    "spoofmail.de", "squizzy.de", "ssoia.com",
    "startkeys.com", "stinkefinger.net", "stop-my-spam.cf",
    "stop-my-spam.com", "stop-my-spam.ga", "stop-my-spam.ml",
    "stop-my-spam.tk", "streetwisemail.com", "stuffmail.de",
    "supergreatmail.com", "supermailer.jp", "superrito.com",
    "superstachel.de", "suremail.info", "svk.jp",
    "sweetxxx.de", "tafmail.com", "tagyourself.com",
    "talkinator.com", "tapchicuoihoi.com", "techemail.com",
    "techgroup.me", "teewars.org", "teleosaurs.xyz",
    "teleworm.com", "teleworm.us", "temp-mail.de",
    "temp-mail.org", "temp-mail.ru", "temp.emeraldwebmail.com",
    "temp.headstrong.de", "tempail.com", "tempalias.com",
    "tempe-mail.com", "tempemail.biz", "tempemail.co.za",
    "tempemail.com", "tempemail.net", "tempinbox.co.uk",
    "tempinbox.com", "tempmail.co", "tempmail.de",
    "tempmail.it", "tempmail.net", "tempmail.us",
    "tempmail2.com", "tempmaildemo.com", "tempmailer.com",
    "tempmailer.de", "tempmailr.com", "temporarioemail.com.br",
    "temporaryemail.net", "temporaryemail.us", "temporaryforwarding.com",
    "temporaryinbox.com", "temporarymailaddress.com", "tempthe.net",
    "temptmail.com", "thanksnospam.info", "thankyou2010.com",
    "thc.st", "thelimestones.com", "thisisnotmyrealemail.com",
    "thismail.net", "thismail.ru", "throam.com",
    "throwam.com", "throwawayemailaddress.com", "throwawaymail.com",
    "tilien.com", "tittbit.in", "tmailinator.com",
    "toiea.com", "toomail.biz", "topranklist.de",
    "tradermail.info", "trash-amil.com", "trash-mail.at",
    "trash-mail.cf", "trash-mail.com", "trash-mail.de",
    "trash-mail.ga", "trash-mail.gq", "trash-mail.ml",
    "trash-mail.tk", "trash2009.com", "trash2010.com",
    "trash2011.com", "trashbin.cf", "trashbox.eu",
    "trashcanmail.com", "trashdevil.com", "trashdevil.de",
    "trashemail.de", "trashmail.at", "trashmail.com",
    "trashmail.de", "trashmail.me", "trashmail.net",
    "trashmail.org", "trashmail.ws", "trashmailer.com",
    "trashymail.com", "trashymail.net", "trbvm.com",
    "trickmail.net", "trillianpro.com", "tryalert.com",
    "turual.com", "twinmail.de", "twoweirdtricks.com",
    "tyldd.com", "uggsrock.com", "umail.net",
    "upliftnow.com", "uplipht.com", "uroid.com",
    "us.af", "valemail.net", "venompen.com",
    "veryrealemail.com", "viditag.com", "viralplays.com",
    "vkcode.ru", "vpn.st", "vsimcard.com",
    "vubby.com", "wasteland.rfc822.org", "webemail.me",
    "webm4il.info", "webuser.in", "wee.my",
    "weg-werf-email.de", "wegwerf-email-addressen.de", "wegwerf-emails.de",
    "wegwerfadresse.de", "wegwerfemail.com", "wegwerfemail.de",
    "wegwerfmail.de", "wegwerfmail.info", "wegwerfmail.net",
    "wegwerfmail.org", "wetrainbayarea.com", "wetrainbayarea.org",
    "wh4f.org", "whatiaas.com", "whatpaas.com",
    "whopy.com", "whtjddn.33mail.com", "whyspam.me",
    "wilemail.com", "willhackforfood.biz", "willselfdestruct.com",
    "winemaven.info", "wolfsmail.tk", "wollan.info",
    "worldspace.link", "wronghead.com", "wuzup.net",
    "wuzupmail.net", "wwwnew.eu", "xagloo.com",
    "xemaps.com", "xents.com", "xmaily.com",
    "xoxy.net", "yapped.net", "yep.it",
    "yogamaven.com", "yopmail.com", "yopmail.fr",
    "yopmail.net", "yourdomain.com", "ypmail.webarnak.fr.eu.org",
    "yuurok.com", "z1p.biz", "za.com",
    "zehnminuten.de", "zehnminutenmail.de", "zetmail.com",
    "zippymail.info", "zoaxe.com", "zoemail.com",
    "zoemail.net", "zoemail.org", "zomg.info",
    "zxcv.com", "zxcvbnm.com", "zzz.com",
}

# Role-based email prefixes (generic emails, not personal)
ROLE_BASED_PREFIXES = {
    # General/Generic
    "info", "contact", "hello", "hi", "hey",
    "mail", "email", "inbox", "office", "general",
    
    # Support
    "support", "help", "helpdesk", "service", "customerservice",
    "customer", "care", "customercare", "assist", "assistance",
    
    # Sales
    "sales", "sell", "selling", "deals", "business",
    "biz", "commercial", "trade", "orders", "order",
    
    # Administration
    "admin", "administrator", "root", "sysadmin", "postmaster",
    "webmaster", "hostmaster", "abuse", "noc", "security",
    
    # Marketing
    "marketing", "market", "promo", "promotions", "newsletter",
    "news", "press", "media", "pr", "publicrelations",
    
    # Human Resources
    "hr", "humanresources", "jobs", "careers", "recruiting",
    "recruitment", "talent", "hiring", "apply", "applications",
    
    # Finance/Billing
    "billing", "finance", "accounts", "accounting", "invoices",
    "payments", "pay", "payroll", "ap", "ar",
    
    # Technical
    "tech", "technical", "it", "itsupport", "dev",
    "developer", "developers", "engineering", "ops", "devops",
    
    # Legal
    "legal", "compliance", "privacy", "gdpr", "dmca",
    "copyright", "trademark", "ip",
    
    # Feedback
    "feedback", "suggestions", "complaints", "survey", "research",
    
    # No-reply
    "noreply", "no-reply", "donotreply", "do-not-reply", "mailer-daemon",
    
    # Team aliases
    "team", "staff", "crew", "group", "all",
    "everyone", "company", "corporate", "headquarters", "hq",
    
    # Misc
    "subscribe", "unsubscribe", "list", "lists", "announce",
    "announcements", "updates", "alerts", "notifications", "notify",
}

# Free email providers (personal email domains, often lower quality for B2B)
FREE_EMAIL_PROVIDERS = {
    # Major providers
    "gmail.com", "googlemail.com",
    "yahoo.com", "yahoo.co.uk", "yahoo.fr", "yahoo.de", "yahoo.es",
    "yahoo.it", "yahoo.ca", "yahoo.com.br", "yahoo.co.in", "yahoo.co.jp",
    "hotmail.com", "hotmail.co.uk", "hotmail.fr", "hotmail.de", "hotmail.es",
    "hotmail.it", "hotmail.ca", "hotmail.com.br",
    "outlook.com", "outlook.co.uk", "outlook.fr", "outlook.de", "outlook.es",
    "live.com", "live.co.uk", "live.fr", "live.de", "live.nl",
    "msn.com",
    
    # Apple
    "icloud.com", "me.com", "mac.com",
    
    # AOL
    "aol.com", "aim.com",
    
    # Other major free providers
    "protonmail.com", "protonmail.ch", "proton.me", "pm.me",
    "tutanota.com", "tutanota.de", "tuta.io",
    "zoho.com", "zohomail.com",
    "mail.com", "email.com",
    "gmx.com", "gmx.net", "gmx.de", "gmx.at", "gmx.ch",
    "web.de", "freenet.de", "t-online.de",
    "yandex.com", "yandex.ru", "ya.ru",
    "mail.ru", "inbox.ru", "list.ru", "bk.ru",
    "rambler.ru",
    
    # Regional providers
    "qq.com", "163.com", "126.com", "sina.com", "sohu.com",
    "naver.com", "hanmail.net", "daum.net",
    "rediffmail.com",
    "laposte.net", "orange.fr", "sfr.fr", "free.fr",
    "libero.it", "virgilio.it", "alice.it", "tin.it", "tiscali.it",
    "wanadoo.fr", "numericable.fr", "bbox.fr",
    "comcast.net", "verizon.net", "att.net", "sbcglobal.net",
    "cox.net", "charter.net", "earthlink.net",
    "btinternet.com", "sky.com", "talktalk.net", "virgin.net",
    "bigpond.com", "optusnet.com.au", "telstra.com",
    
    # Other free services
    "fastmail.com", "fastmail.fm",
    "hushmail.com",
    "runbox.com",
    "posteo.de", "posteo.net",
    "disroot.org",
    "riseup.net",
    "autistici.org",
}


def is_disposable_domain(domain: str) -> bool:
    """Check if a domain is a known disposable/temporary email domain."""
    return domain.lower() in DISPOSABLE_DOMAINS


def is_role_based_email(email: str) -> bool:
    """Check if an email is role-based (generic, not personal)."""
    local_part = email.split("@")[0].lower()
    return local_part in ROLE_BASED_PREFIXES


def is_free_provider(domain: str) -> bool:
    """Check if a domain is a free email provider."""
    return domain.lower() in FREE_EMAIL_PROVIDERS


def get_blocklist_info(email: str) -> dict:
    """
    Get comprehensive blocklist information for an email.
    
    Returns:
        dict with is_disposable, is_role_based, is_free_provider flags
    """
    local_part = email.split("@")[0].lower()
    domain = email.split("@")[-1].lower()
    
    return {
        "is_disposable": is_disposable_domain(domain),
        "is_role_based": is_role_based_email(email),
        "is_free_provider": is_free_provider(domain),
    }

