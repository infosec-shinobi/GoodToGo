# Digital-Life Guide Catalog

Status: Initial curated catalog  
Last reviewed: 2026-09-11

The application should link users to primary provider instructions rather than copying
procedures that will become stale. The machine-readable source is
`app/content/core_us/digital_guides.yaml`.

## Preparation guides

| Provider | Action | Official guide |
| --- | --- | --- |
| Google | Configure trusted contacts, shared data, inactivity timing, and deletion | [Inactive Account Manager](https://support.google.com/accounts/answer/3036546) |
| Apple | Add a Legacy Contact and preserve the access key | [Add a Legacy Contact](https://support.apple.com/en-us/102631) |
| Bitwarden | Configure a trusted emergency contact, access type, and waiting period | [Emergency Access](https://bitwarden.com/help/emergency-access/) |
| 1Password | Download and secure an Emergency Kit | [Emergency Kit](https://support.1password.com/emergency-kit/) |
| 1Password | Ensure multiple family organizers can perform recovery | [Family account recovery](https://support.1password.com/recovery/) |
| Facebook | Choose a Legacy Contact for a memorialized account | [Legacy Contact help](https://www.facebook.com/help/1568013990080948) |
| GitHub | Designate an account successor and document repository wishes | [Deceased User Policy](https://docs.github.com/en/site-policy/other-site-policies/github-deceased-user-policy) |

## Survivor guides

| Provider | Action | Official guide |
| --- | --- | --- |
| Google | Request eligible data, funds, or account closure | [Deceased user request](https://support.google.com/accounts/troubleshooter/6357590) |
| X | Request deactivation as authorized estate representative or verified immediate family | [Deceased family member account](https://help.x.com/en/rules-and-policies/contact-x-about-a-deceased-family-members-account) |
| PayPal | Close an account and address remaining funds through the executor or administrator | [Deceased relative account](https://www.paypal.com/us/cshelp/article/how-do-i-close-the-paypal-account-of-a-deceased-relative-help220) |

## Legal reference

- [Ohio Uniform Fiduciary Access to Digital Assets Act](https://codes.ohio.gov/ohio-revised-code/chapter-2137)

The Ohio statute distinguishes provider online tools, directions in wills and other
records, fiduciary authority, account terms, and legal access to electronic
communications. The application should prompt for both provider settings and legal-plan
review instead of treating a password list as sufficient authorization.

## Guide-record fields

- Stable ID
- Provider
- Title
- URL
- Purpose: prepare, survivor, or reference
- Jurisdiction
- Summary
- Last verified date
- Last content review date
- Replacement URL if retired
- Applicability conditions

## Maintenance process

1. Check every URL at least quarterly.
2. Review provider instructions at least annually and after reported policy changes.
3. Prefer official support or legal sources.
4. Mark inaccessible or region-specific guides rather than silently substituting a blog.
5. Version task behavior when a provider changes available options.
6. Do not scrape authenticated account settings or send users' account details to a
   provider.

## Additional providers to research before content-complete release

- Microsoft account, Outlook, OneDrive, and Xbox
- Instagram and Threads
- LinkedIn
- Dropbox
- Amazon and Kindle
- Major mobile carriers
- Major domain registrars and DNS providers
- Common cryptocurrency custody models
- Steam, PlayStation, and Nintendo
- Major photo-storage providers
- Common self-hosted password managers

These should be added only after the exact official URL and current policy are verified.

