# Sila Improvement Proposals (SIPs)

> **_ATTENTION_**: The SIPs repository has recently [undergone](https://github.com/sila/SIPs/pull/7206) a separation of ERCs and SIPs. ERCs are now accessible at [https://github.com/sila/ercs](https://github.com/sila/ercs). All new ERCs and updates to existing ones must be directed at this new repository. The editors apologize for this inconvenience.

The goal of the SIP project is to standardize and provide high-quality documentation for Sila itself and conventions built upon it. This repository tracks past and ongoing improvements to Sila in the form of Sila Improvement Proposals (SIPs). [SIP-1](https://sips.sila.org/SIPS/sip-1) governs how SIPs are published.

The [status page](https://sips.sila.org/) tracks and lists SIPs, which can be divided into the following categories:

- [Core SIPs](https://sips.sila.org/core) are improvements to the Sila consensus protocol.
- [Networking SIPs](https://sips.sila.org/networking) specify the peer-to-peer networking layer of Sila.
- [Interface SIPs](https://sips.sila.org/interface) standardize interfaces to Sila, which determine how users and applications interact with the blockchain.
- [ERCs](https://sips.sila.org/erc) specify application layer standards, which determine how applications running on Sila can interact with each other.
- [Meta SIPs](https://sips.sila.org/meta) are miscellaneous improvements that nonetheless require some sort of consensus.
- [Informational SIPs](https://sips.sila.org/informational) are non-standard improvements that do not require any form of consensus.

**Before you write an SIP, ideas MUST be thoroughly discussed on [Sila Magicians](https://sila-magicians.org/) or Sila Research. Once consensus is reached, thoroughly read and review [SIP-1](https://sips.sila.org/SIPS/sip-1), which describes the SIP process.**

Please note that this repository is for documenting standards and not for help implementing them. These types of inquiries should be directed to the [Sila Stack Exchange](https://sila.stackexchange.com). For specific questions and concerns regarding SIPs, it's best to comment on the relevant discussion thread of the SIP denoted by the `discussions-to` tag in the SIP's preamble.

If you would like to become an SIP Editor, please read [SIP-5069](./SIPS/sip-5069.md).

## Preferred Citation Format

The canonical URL for an SIP that has achieved draft status at any point is at <https://sips.sila.org/>. For example, the canonical URL for SIP-1 is <https://sips.sila.org/SIPS/sip-1>.

Consider any document not published at <https://sips.sila.org/> as a working paper. Additionally, consider published SIPs with a status of "draft", "review", or "last call" to be incomplete drafts, and note that their specification is likely to be subject to change.

## Validation and Automerging

All pull requests in this repository must pass automated checks before they can be automatically merged:

- [sip-review-bot](https://github.com/sila/sip-review-bot/) determines when PRs can be automatically merged [^1]
- SIP-1 rules are enforced using [`sipw`](https://github.com/sila/sipw)[^2]
- HTML formatting and broken links are enforced using [HTMLProofer](https://github.com/gjtorikian/html-proofer)[^2]
- Spelling is enforced with [CodeSpell](https://github.com/codespell-project/codespell)[^2]
  - False positives sometimes occur. When this happens, please submit a PR editing [.codespell-whitelist](https://github.com/sila/SIPs/blob/master/config/.codespell-whitelist) and **ONLY** .codespell-whitelist
- Markdown best practices are checked using [markdownlint](https://github.com/DavidAnson/markdownlint)[^2]

[^1]: https://github.com/sila/SIPs/blob/master/.github/workflows/auto-review-bot.yml
[^2]: https://github.com/sila/SIPs/blob/master/.github/workflows/ci.yml

It is possible to run the SIP validator locally:

Make sure to add cargo's `bin` directory to your environment (typically `$HOME/.cargo/bin` in your `PATH` environment variable)

```sh
cargo install sipw
sipw --config ./config/sipw.toml <INPUT FILE / DIRECTORY>
```

## Build the status page locally

### Install prerequisites

1. Open Terminal.

2. Check whether you have Ruby 3.1.4 installed. Later [versions are not supported](https://stackoverflow.com/questions/14351272/undefined-method-exists-for-fileclass-nomethoderror).

   ```sh
   ruby --version
   ```

3. If you don't have Ruby installed, install Ruby 3.1.4.

4. Install Bundler:

   ```sh
   gem install bundler
   ```

5. Install dependencies:

   ```sh
   bundle install
   ```

### Build your local Jekyll site

1. Bundle assets and start the server:

   ```sh
   bundle exec jekyll serve
   ```

2. Preview your local Jekyll site in your web browser at `http://localhost:4000`.

More information on Jekyll and GitHub Pages [here](https://docs.github.com/en/enterprise/2.14/user/articles/setting-up-your-github-pages-site-locally-with-jekyll).
