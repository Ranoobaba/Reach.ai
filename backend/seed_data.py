"""
Seed data for pre-populating the cache with known company email domains.
Run this script to add common companies to the cache.
"""

from database import bulk_import_domains, get_cache_stats

# Common tech companies with their email domains
SEED_COMPANIES = [
    # AI/ML Companies
    {"company_name": "Adept", "email_domain": "adept.ai", "website_url": "https://www.adept.ai"},
    {"company_name": "AI21 Labs", "email_domain": "ai21.com", "website_url": "https://www.ai21.com"},
    {"company_name": "Anyscale", "email_domain": "anyscale.com", "website_url": "https://www.anyscale.com"},
    {"company_name": "Anthropic", "email_domain": "anthropic.com", "website_url": "https://www.anthropic.com"},
    {"company_name": "Arize AI", "email_domain": "arize.com", "website_url": "https://arize.com"},
    {"company_name": "AssemblyAI", "email_domain": "assemblyai.com", "website_url": "https://www.assemblyai.com"},
    {"company_name": "Baseten", "email_domain": "baseten.co", "website_url": "https://baseten.co"},
    {"company_name": "Braintrust", "email_domain": "braintrust.dev", "website_url": "https://www.braintrust.dev"},
    {"company_name": "Cartage", "email_domain": "cartage.ai", "website_url": "https://www.cartage.ai"},
    {"company_name": "Cerebras", "email_domain": "cerebras.net", "website_url": "https://cerebras.net"},
    {"company_name": "Chroma", "email_domain": "trychroma.com", "website_url": "https://www.trychroma.com"},
    {"company_name": "Cognition", "email_domain": "cognition.ai", "website_url": "https://www.cognition.ai"},
    {"company_name": "Cohere", "email_domain": "cohere.com", "website_url": "https://cohere.com"},
    {"company_name": "CoreWeave", "email_domain": "coreweave.com", "website_url": "https://www.coreweave.com"},
    {"company_name": "Cursor", "email_domain": "cursor.com", "website_url": "https://cursor.com"},
    {"company_name": "Databricks", "email_domain": "databricks.com", "website_url": "https://www.databricks.com"},
    {"company_name": "Databricks (Mosaic AI Research)", "email_domain": "databricks.com", "website_url": "https://www.databricks.com"},
    {"company_name": "DeepSeek", "email_domain": "deepseek.com", "website_url": "https://www.deepseek.com"},
    {"company_name": "Deepgram", "email_domain": "deepgram.com", "website_url": "https://deepgram.com"},
    {"company_name": "Docker", "email_domain": "docker.com", "website_url": "https://www.docker.com"},
    {"company_name": "ElevenLabs", "email_domain": "elevenlabs.io", "website_url": "https://elevenlabs.io"},
    {"company_name": "Exa", "email_domain": "exa.ai", "website_url": "https://exa.ai"},
    {"company_name": "Firecrawl", "email_domain": "firecrawl.dev", "website_url": "https://www.firecrawl.dev"},
    {"company_name": "Fireworks AI", "email_domain": "fireworks.ai", "website_url": "https://fireworks.ai"},
    {"company_name": "Gensyn", "email_domain": "gensyn.ai", "website_url": "https://www.gensyn.ai"},
    {"company_name": "Glean", "email_domain": "glean.com", "website_url": "https://www.glean.com"},
    {"company_name": "Google DeepMind", "email_domain": "google.com", "website_url": "https://deepmind.google"},
    {"company_name": "Gretel", "email_domain": "gretel.ai", "website_url": "https://gretel.ai"},
    {"company_name": "Groq", "email_domain": "groq.com", "website_url": "https://groq.com"},
    {"company_name": "HappyRobot", "email_domain": "happyrobot.ai", "website_url": "https://www.happyrobot.ai"},
    {"company_name": "Hedra", "email_domain": "hedra.com", "website_url": "https://www.hedra.com"},
    {"company_name": "Helicone", "email_domain": "helicone.ai", "website_url": "https://www.helicone.ai"},
    {"company_name": "HeyGen", "email_domain": "heygen.com", "website_url": "https://www.heygen.com"},
    {"company_name": "HackerRank", "email_domain": "hackerrank.com", "website_url": "https://www.hackerrank.com"},
    {"company_name": "Hugging Face", "email_domain": "huggingface.co", "website_url": "https://huggingface.co"},
    {"company_name": "Humanloop", "email_domain": "humanloop.com", "website_url": "https://humanloop.com"},
    {"company_name": "Labelbox", "email_domain": "labelbox.com", "website_url": "https://labelbox.com"},
    {"company_name": "Lambda", "email_domain": "lambda.ai", "website_url": "https://lambda.ai"},
    {"company_name": "LangChain", "email_domain": "langchain.dev", "website_url": "https://www.langchain.com"},
    {"company_name": "Langfuse", "email_domain": "langfuse.com", "website_url": "https://langfuse.com"},
    {"company_name": "LlamaIndex", "email_domain": "llamaindex.ai", "website_url": "https://www.llamaindex.ai"},
    {"company_name": "Luma", "email_domain": "lumalabs.ai", "website_url": "https://lumalabs.ai"},
    {"company_name": "Magic", "email_domain": "magic.dev", "website_url": "https://magic.dev"},
    {"company_name": "Middleware", "email_domain": "middleware.io", "website_url": "https://middleware.io"},
    {"company_name": "Midjourney", "email_domain": "midjourney.com", "website_url": "https://www.midjourney.com"},
    {"company_name": "Mistral AI", "email_domain": "mistral.ai", "website_url": "https://mistral.ai"},
    {"company_name": "Modal", "email_domain": "modal.com", "website_url": "https://modal.com"},
    {"company_name": "Moonshot AI", "email_domain": "moonshot.ai", "website_url": "https://www.moonshot.ai"},
    {"company_name": "OpenAI", "email_domain": "openai.com", "website_url": "https://openai.com"},
    {"company_name": "OpenPipe", "email_domain": "openpipe.ai", "website_url": "https://openpipe.ai"},
    {"company_name": "OpenRouter", "email_domain": "openrouter.ai", "website_url": "https://openrouter.ai"},
    {"company_name": "Perplexity", "email_domain": "perplexity.ai", "website_url": "https://www.perplexity.ai"},
    {"company_name": "Photoroom", "email_domain": "photoroom.com", "website_url": "https://www.photoroom.com"},
    {"company_name": "Pika", "email_domain": "pika.art", "website_url": "https://pika.art"},
    {"company_name": "Pinecone", "email_domain": "pinecone.io", "website_url": "https://www.pinecone.io"},
    {"company_name": "Portkey", "email_domain": "portkey.ai", "website_url": "https://portkey.ai"},
    {"company_name": "Predibase", "email_domain": "predibase.com", "website_url": "https://predibase.com"},
    {"company_name": "PromptLayer", "email_domain": "promptlayer.com", "website_url": "https://promptlayer.com"},
    {"company_name": "Pump", "email_domain": "pump.co", "website_url": "https://www.pump.co"},
    {"company_name": "Qdrant", "email_domain": "qdrant.tech", "website_url": "https://qdrant.tech"},
    {"company_name": "Reka AI", "email_domain": "reka.ai", "website_url": "https://reka.ai"},
    {"company_name": "Replicate", "email_domain": "replicate.com", "website_url": "https://replicate.com"},
    {"company_name": "Retell AI", "email_domain": "retellai.com", "website_url": "https://www.retellai.com"},
    {"company_name": "RunPod", "email_domain": "runpod.io", "website_url": "https://www.runpod.io"},
    {"company_name": "Runway", "email_domain": "runwayml.com", "website_url": "https://runwayml.com"},
    {"company_name": "Sakana AI", "email_domain": "sakana.ai", "website_url": "https://sakana.ai"},
    {"company_name": "Scale AI", "email_domain": "scale.com", "website_url": "https://scale.com"},
    {"company_name": "Snorkel AI", "email_domain": "snorkel.ai", "website_url": "https://snorkel.ai"},
    {"company_name": "Stability AI", "email_domain": "stability.ai", "website_url": "https://stability.ai"},
    {"company_name": "Stripe", "email_domain": "stripe.com", "website_url": "https://stripe.com"},
    {"company_name": "Suno", "email_domain": "suno.com", "website_url": "https://suno.com"},
    {"company_name": "Surge AI", "email_domain": "surgehq.ai", "website_url": "https://surgehq.ai"},
    {"company_name": "Synthesia", "email_domain": "synthesia.io", "website_url": "https://www.synthesia.io"},
    {"company_name": "Tavily", "email_domain": "tavily.com", "website_url": "https://tavily.com"},
    {"company_name": "Together AI", "email_domain": "together.ai", "website_url": "https://www.together.ai"},
    {"company_name": "Unstructured", "email_domain": "unstructured.io", "website_url": "https://unstructured.io"},
    {"company_name": "Vapi", "email_domain": "vapi.ai", "website_url": "https://vapi.ai"},
    {"company_name": "Weaviate", "email_domain": "weaviate.io", "website_url": "https://weaviate.io"},
    {"company_name": "Weights & Biases", "email_domain": "wandb.com", "website_url": "https://wandb.ai"},
    {"company_name": "Writer", "email_domain": "writer.com", "website_url": "https://writer.com"},
    
    # Big Tech
    {"company_name": "Google", "email_domain": "google.com", "website_url": "https://google.com"},
    {"company_name": "Microsoft", "email_domain": "microsoft.com", "website_url": "https://microsoft.com"},
    {"company_name": "Apple", "email_domain": "apple.com", "website_url": "https://apple.com"},
    {"company_name": "Amazon", "email_domain": "amazon.com", "website_url": "https://amazon.com"},
    {"company_name": "Meta", "email_domain": "meta.com", "website_url": "https://meta.com"},
    {"company_name": "Netflix", "email_domain": "netflix.com", "website_url": "https://netflix.com"},
    {"company_name": "Spotify", "email_domain": "spotify.com", "website_url": "https://spotify.com"},
    {"company_name": "Uber", "email_domain": "uber.com", "website_url": "https://uber.com"},
    {"company_name": "Airbnb", "email_domain": "airbnb.com", "website_url": "https://airbnb.com"},
    
    # Developer Tools
    {"company_name": "GitHub", "email_domain": "github.com", "website_url": "https://github.com"},
    {"company_name": "GitLab", "email_domain": "gitlab.com", "website_url": "https://gitlab.com"},
    {"company_name": "Vercel", "email_domain": "vercel.com", "website_url": "https://vercel.com"},
    {"company_name": "Netlify", "email_domain": "netlify.com", "website_url": "https://netlify.com"},
    {"company_name": "Cloudflare", "email_domain": "cloudflare.com", "website_url": "https://cloudflare.com"},
    {"company_name": "DigitalOcean", "email_domain": "digitalocean.com", "website_url": "https://digitalocean.com"},
    {"company_name": "Heroku", "email_domain": "heroku.com", "website_url": "https://heroku.com"},
    {"company_name": "MongoDB", "email_domain": "mongodb.com", "website_url": "https://mongodb.com"},
    {"company_name": "Supabase", "email_domain": "supabase.com", "website_url": "https://supabase.com"},
    {"company_name": "PlanetScale", "email_domain": "planetscale.com", "website_url": "https://planetscale.com"},
    {"company_name": "Prisma", "email_domain": "prisma.io", "website_url": "https://prisma.io"},
    {"company_name": "Datadog", "email_domain": "datadoghq.com", "website_url": "https://datadoghq.com"},
    {"company_name": "Sentry", "email_domain": "sentry.io", "website_url": "https://sentry.io"},
    
    # SaaS/B2B
    {"company_name": "Salesforce", "email_domain": "salesforce.com", "website_url": "https://salesforce.com"},
    {"company_name": "HubSpot", "email_domain": "hubspot.com", "website_url": "https://hubspot.com"},
    {"company_name": "Zendesk", "email_domain": "zendesk.com", "website_url": "https://zendesk.com"},
    {"company_name": "Intercom", "email_domain": "intercom.com", "website_url": "https://intercom.com"},
    {"company_name": "Slack", "email_domain": "slack.com", "website_url": "https://slack.com"},
    {"company_name": "Notion", "email_domain": "notion.so", "website_url": "https://notion.so"},
    {"company_name": "Figma", "email_domain": "figma.com", "website_url": "https://figma.com"},
    {"company_name": "Canva", "email_domain": "canva.com", "website_url": "https://canva.com"},
    {"company_name": "Airtable", "email_domain": "airtable.com", "website_url": "https://airtable.com"},
    {"company_name": "Asana", "email_domain": "asana.com", "website_url": "https://asana.com"},
    {"company_name": "Monday.com", "email_domain": "monday.com", "website_url": "https://monday.com"},
    {"company_name": "Zoom", "email_domain": "zoom.us", "website_url": "https://zoom.us"},
    {"company_name": "Twilio", "email_domain": "twilio.com", "website_url": "https://twilio.com"},
    {"company_name": "SendGrid", "email_domain": "sendgrid.com", "website_url": "https://sendgrid.com"},
    {"company_name": "Mailchimp", "email_domain": "mailchimp.com", "website_url": "https://mailchimp.com"},
    
    # Fintech
    {"company_name": "Plaid", "email_domain": "plaid.com", "website_url": "https://plaid.com"},
    {"company_name": "Square", "email_domain": "squareup.com", "website_url": "https://squareup.com"},
    {"company_name": "Robinhood", "email_domain": "robinhood.com", "website_url": "https://robinhood.com"},
    {"company_name": "Coinbase", "email_domain": "coinbase.com", "website_url": "https://coinbase.com"},
    {"company_name": "Brex", "email_domain": "brex.com", "website_url": "https://brex.com"},
    {"company_name": "Ramp", "email_domain": "ramp.com", "website_url": "https://ramp.com"},
    
    # E-commerce
    {"company_name": "Shopify", "email_domain": "shopify.com", "website_url": "https://shopify.com"},
    {"company_name": "Etsy", "email_domain": "etsy.com", "website_url": "https://etsy.com"},
    {"company_name": "eBay", "email_domain": "ebay.com", "website_url": "https://ebay.com"},
    
    # Security
    {"company_name": "CrowdStrike", "email_domain": "crowdstrike.com", "website_url": "https://crowdstrike.com"},
    {"company_name": "Okta", "email_domain": "okta.com", "website_url": "https://okta.com"},
    {"company_name": "Auth0", "email_domain": "auth0.com", "website_url": "https://auth0.com"},
    {"company_name": "1Password", "email_domain": "1password.com", "website_url": "https://1password.com"},
]


def seed_database():
    """Seed the database with initial company data."""
    print(f"Seeding database with {len(SEED_COMPANIES)} companies...")
    bulk_import_domains(SEED_COMPANIES)
    
    stats = get_cache_stats()
    print(f"\nDatabase now has {stats['total_entries']} entries")
    print("\nTop 10 entries:")
    for entry in stats['recently_added'][:10]:
        print(f"  - {entry['company_name']} → {entry['email_domain']}")


if __name__ == "__main__":
    seed_database()
