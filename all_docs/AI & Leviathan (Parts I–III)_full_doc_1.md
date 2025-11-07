# AI and Leviathan: Part I

_The institutional economics of an intelligence explosion_

**Author:** Samuel Hammond
**Published:** August 23, 2023
**URL:** https://www.secondbest.ca/p/ai-and-leviathan-part-i

---

Imagine a breakthrough happened and suddenly everyone had access to cheap, x-ray style glasses. The glasses look like normal, everyday glasses, but come with a dial setting that lets you see through walls, people's clothing, etc. It somehow works on old photos and video recordings too.

On one level, this would be amazing. You might notice the mysterious lump on your friend’s thyroid, say, catching their cancer early and saving them untold medical costs. But in the immediate term, universal and near-undetectable access to the glasses (or contact lenses, if you prefer) would be a security and privacy disaster. No one's home or device security was compromised per se. Rather, it's more like a society designed around the visible light spectrum became maladapted overnight.

There are three canonical ways that society could respond:

1. **Cultural evolution**: we embrace nudism and a variety of new, post-privacy norms;
2. **Mitigation and adaptation**: we start wearing lead underwear and scramble to retrofit our homes, office buildings, and locker rooms with impenetrable walls;
3. **Regulation and enforcement**: we ban or tightly regulate the technology and build an x-ray Leviathan for inspecting people's glasses, punishing violators, etc.

The option where everyone spontaneously coordinates to never use the glasses, or to only use them for a subset of pro-social purposes, is unstable. Even if you're a voyeur and access to the glasses benefits you personally, there's an underlying prisoner's dilemma, and so we quickly shift to the equilibrium where everyone has the glasses even if we all preferred the world without them.

The glasses are a metaphor for Artificial Intelligence.

It’s barely a metaphor. AI already unlocks a kind of x-ray vision via the [displacement of WiFi signals](https://www.vice.com/en/article/y3p7xj/scientists-are-getting-eerily-good-at-using-wifi-to-see-people-through-walls-in-detail) in a room, and with a few IR sensors you’ll eventually be able to interpolate accurate nude bodies onto every pedestrian in Times Square. The nudist AR filter won’t be allowed in the Apple VisonPro app store, but the basic technology will be sufficiently cheap and open source to make that a moot point.

## Signal extraction

AI is a microscope. **It increases the information resolution of the universe.** This has many amazing implications but also many scary one.

AI lets us [refactor legacy code](https://understandlegacycode.com/blog/can-ai-refactor-legacy-code/), [restore ancient scrolls](https://scrollprize.org/), and [detect new galaxies](https://phys.org/news/2022-07-ai-assisted-analysis-three-dimensional-galaxy-universe.html) in old astronomical surveys. At the same time, AI turns your [gait into a finger print](https://apnews.com/article/bf75dd1c26c947b7826d270a16e2658a), [a microphone into a key logger](https://arstechnica.com/gadgets/2023/08/type-softly-researchers-can-guess-keystrokes-by-sound-with-93-accuracy/), and a snapshot of your face into a [> 93% accurate polygraph test](https://link.springer.com/chapter/10.1007/978-3-031-03884-6_29).

[![](https://substackcdn.com/image/fetch/$s_!WKyg!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F06730bc7-00f9-4b35-afc7-09a1e394fc99_1258x703.png)](https://substackcdn.com/image/fetch/$s_!WKyg!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F06730bc7-00f9-4b35-afc7-09a1e394fc99_1258x703.png)

Jiaqi Geng et al. (2022) “[DensePose from WiFi](https://arxiv.org/abs/2301.00250)”

While deepfakes are a growing concern, AI is overall making the world radically less opaque. Perfect transparency has costs of its own. Knowledge will expand and barriers to manipulating the world will decrease. We will literally hear the cries of [stressed out flowers](https://www.nature.com/articles/d41586-023-00890-9) and have [conversations with whales](https://www.youtube.com/watch?v=N34ZK6QLWbE). Then, one day, an AI model for completing your sentences will learn to finish your thoughts, smashing the subjective divide that much of Western philosophy assumed was impenetrable.

Many of these use-cases aren’t new, but are only now getting reliable thanks to scaling. If there is signal in the noise, a big enough neural network will extract it, and in a way that’s getting exponentially cheaper and easier to access overtime. You won’t even have to `pip install`! Your Jarvis-like AI assistant will simply call up bespoke models from HuggingFace or GitHub on demand. For the DnD players out there, it will be like an amulet that grants its wearer a natural 20 on every arcana check.

This sounds liberating, and in many ways it will be. But history also suggest that enhancements to our natural liberty can be paradoxically oppressive, at least in the short run.

To be clear, what follows is not an argument for pausing AI development, even if we could. While I think we will need new oversight mechanisms for deploying frontier models safely as their [scale and power](https://epochai.org/blog/extrapolating-performance-in-language-modelling-benchmarks) ramps up, our goal should not be to stop AI but rather to in some sense [master it](https://www.politico.com/news/magazine/2023/05/08/manhattan-project-for-ai-safety-00095779).

If anything, accelerating the different modalities of defensive AI may be our best hope for making the “mitigation and adaptation” option the path of less resistance. Nevertheless, it’s important to be clear about the many ways in which our AI future is [a package deal](https://www.cato-unbound.org/2007/03/11/tyler-cowen/paradox-libertarianism/), and to draw out the implications for the likely evolution of our social order without prejudice.

## The State of Nature

Thomas Hobbes famously described life in the “state of nature” as a “war of all against all.” This is sometimes confused as a claim about hunter-gather societies, but Hobbes was actually alluding to the catastrophic conditions of the English Civil War, from which he fled for his personal safety. _[Leviathan](<https://en.wikipedia.org/wiki/Leviathan_(Hobbes_book)>)_ was first published in 1651, near the start of the Interregnum. Having perceived the war’s origins in the growing fragmentation and radicalization of English society under the tenuous, personal rule of King Charles I, _Leviathan_ provided a theoretical argument for why absolute monarchy was the only way to restore peace and order. Hobbes’ notion of a social “covenant” wasn’t a [literal contract](https://iep.utm.edu/soc-cont/) that individuals signed, but rather an abstract description of the process whereby warring factions achieve a political settlement by ceding their “natural liberty” to interfere in each other’s affairs to a higher authority.

The proximate causes of the English Civil War are complex and manifold, but the macro story is one of [disruptive technological change](https://www.sciencedirect.com/science/article/abs/pii/S0014292121001641). While the printing press was invented two centuries prior, the War occurred at the inflection of the printing _revolution_ — the point of criticality that unlocked take-off growth in printed outputs. The first publication of the King James Bible was in 1611, for example, just 30 years before the war but only 55 years before the [birth of journalism](http://thehistorypress.co.uk/articles/the-english-civil-war-and-the-rise-of-journalism/) with the first regularly published English newspaper, the _[The Oxford Gazette](https://en.wikipedia.org/wiki/The_London_Gazette)_.

[![](https://substackcdn.com/image/fetch/$s_!SZTg!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fb02a3623-1c99-4698-b06d-c8624ab2cc6a_1432x983.png)](https://substackcdn.com/image/fetch/$s_!SZTg!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fb02a3623-1c99-4698-b06d-c8624ab2cc6a_1432x983.png)

Jeremiah Dittmar (2011) "[The Welfare Impact of a New Good: The Printed Book](https://www.semanticscholar.org/paper/The-Welfare-Impact-of-a-New-Good%3A-The-Printed-Book-Dittmar/939bb19e943dfc478359f74b5c7bc87c2034230a)"

Widespread access to printing enabled equally widespread dissent, spurring a “[revolt of the public](https://press.stripe.com/the-revolt-of-the-public)” that mirrored the dynamics Martin Gurri attributes to the internet era. From the English Reformation on, growing access to information thus not only broadened people’s minds to alternative [political allegiances](https://www.jstor.org/stable/25472844), but made them increasingly aware of their differently-thinking neighbors. When Parliament’s legal controls over the press [all but collapsed](https://www.jstor.org/stable/41999120?read-now=1&oauth_data=eyJlbWFpbCI6InNhbXVlbHBoYW1tb25kQGdtYWlsLmNvbSIsImluc3RpdHV0aW9uSWRzIjpbXSwicHJvdmlkZXIiOiJnb29nbGUifQ&seq=3#page_scan_tab_contents) in 1643, its episcopal licensing and censorship regime was turned over to an unregulated market, making it even easier for Puritan separatists, Independents and other radical nonconformists to find likeminded others and coordinate against the Church. The Parliament, meanwhile, was itself contesting the authority of the Crown, creating what the historian Robert Zaller called a new “[discourse of legitimacy](https://www.sup.org/books/title/?id=10148).” Over a few dizzyingly short years, ideological escalation across multiple fronts finally reached its denouement in regicide and mass violence.

AI is often compared to the printing press, but the parallels between Early Modern England and contemporary America extend beyond the technological. Our cultural and ideological schisms are intensifying; the new Puritans have run headlong into a conservative counter-reaction; and our parliamentary debates revolve around issues of censorship as the prior century’s media controls succumb to the open internet. Even the power of the U.S. Presidency has reached its nadir, as if awaiting an [originalist King](https://en.wikipedia.org/wiki/Personal_Rule) to reassert the [unitary executive](https://en.wikipedia.org/wiki/Unitary_executive_theory) and precipitate a crisis.

## Accelerating to what?

These schisms are reflected in the different AI camps. Some favor regulating AI development until we can assure perfect safety, perhaps through a licensing regime. Others wish to plow forward, accelerating access through open source.

The English reformer and “intelligencer,” [Samuel Hartlib](https://en.wikipedia.org/wiki/Samuel_Hartlib#:~:text=Hartlib%20set%20out%20with%20a,to%20modern%20internet%20search%20engines.), was the “effective accelerationist” of his day. It was his stated goal to “record all human knowledge and to make it universally available for the education of all mankind,” and he often printed technical texts to circulate at his own expense — the closest thing to open sourcing at the time. Today’s AI evangelists have similarly lofty goals, from Emad Mostaque’s mission to use AI to [educate the world’s children](https://www.youtube.com/watch?v=h-oF5dWuXAs), to Marc Andreesen’s [vision of AI](https://a16z.com/2023/06/06/ai-will-save-the-world/) as a tool for augmenting humanity across virtually every domain.

The accelerationists have the long view of history on their side, and I broadly support the Andreesen vision of the future. Nonetheless, it is always easier to imagine the end point of a technology than to foresee the trade-offs and forking paths that inevitably arise during the transition.

[George Hotz’s](https://www.youtube.com/shorts/E7jtVW6TypM) _[Chaotic Good](https://easydamus.com/chaoticgood.html)_ instinct to open source potentially dual-use models as quickly as possible has a particularly high potential for blowback. The e/acc ethic is to see open source as pulling forward the advancement of human freedom while validating a DEF CON-style [security mindset](https://security.stackexchange.com/questions/82362/in-citizenfour-what-was-edward-snowden-mitigating-with-a-head-blanket). As more of the economy flows through proprietary models, open source alternatives will also be an essential check on AI becoming monopolized by the state or a handful of tech behemoth.

Fortunately, there is huge middle ground between the safetyist’s “[FDA for AI models](https://rtp.fedsoc.org/blog/the-problem-with-ai-licensing-an-fda-for-algorithms/)” and the rapturous urge to democratize powerful new capabilities the moment the training run ends. If offensive capabilities democratize faster than adaptation and defensive technology can keep up, open source maximalism could even jeopardize the cause of freedom itself, accelerating the conditions for the AI Leviathan that Hotz and company fear most.

## Minority rule

Before 2001, [airport security](https://www.npr.org/2021/09/10/1035131619/911-travel-timeline-tsa) was almost invisible. You could even drive between Canada and the US without a passport. Then, one fateful morning in September, 19 terrorists murdered nearly 3000 people in the span of a few hours. [One week later](https://en.wikipedia.org/wiki/2001_anthrax_attacks), letters containing anthrax spores began showing up in important peoples’ mailboxes, killing five. Eight weeks after that, [Richard Reid](https://www.fbi.gov/history/artifacts/richard-reids-shoes) was caught mid-flight trying to light a bomb hidden in his shoe. Amid this rapid succession of events, our leaders suddenly realized that technology and globalization were introducing a series of _asymmetric_ risks. From bioweapons to hijackings, you now only needed a small group of extremists or a lone radical to wreak havoc across society.

Society responded in all three of the canonical ways listed above. We mitigated risks by fortifying border and airport security. We enhanced enforcement by passing the Patriot Act and funding for new forms of high-tech surveillance. And our culture quickly adapted to the growing [security theater](https://en.wikipedia.org/wiki/Security_theater), buttressed by fears of Islamic radicalism and an eruption in national solidarity.

In retrospect, we over-reacted. While terrorism loomed large psychologically, [the risks were quantifiably small](https://www.amazon.com/Risk-Science-Politics-Fear-gardner-dan/dp/1905264151) compared to the mundane things that kill people every day. In the 12 months after 9/11, for example, the increased fear of flying plausibly caused [an estimated](https://pure.mpg.de/rest/items/item_2101348/component/file_2101347/content) 1,600 excess traffic fatalities. Fear of Islamic terrorism has since subsided, but these enhanced security protocols not only remain in place, but continue to be built upon and even repurposed for [domestic threats](https://www.whitehouse.gov/briefing-room/statements-releases/2023/06/27/fact-sheet-national-strategy-for-countering-domestic-terrorism-strategic-implementation-update/).

[![](https://substackcdn.com/image/fetch/$s_!5E_C!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fde2eaa21-d0ee-4af6-9b95-104f5b43b6a5_1344x896.png)](https://substackcdn.com/image/fetch/$s_!5E_C!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fde2eaa21-d0ee-4af6-9b95-104f5b43b6a5_1344x896.png)

Dangerous misuse of AI will probably be similarly rare. Most people are simply not sociopaths. Nevertheless, many areas of life follow the logic of [Nassim Taleb’s Minority Rule](https://medium.com/incerto/the-most-intolerant-wins-the-dictatorship-of-the-small-minority-3f1f83ce4e15), in which a small but intolerable minority ends up setting the rule for everyone. Fewer than 2% of Americans have a peanut allergy, for example, and yet many d spaces ban foods containing peanuts just to be safe.

Depending on how the offensive-defensive balance shakes out, AI has the potential to return us to a world in which security is once again invisible. You won’t have to remove your shoes and debase yourself before a TSA agent. Instead, a camera will analyze your face as you walk into the terminal, checking it against a database of known bad guys while extracting any predictive signal hidden in your facial expressions, body language, demographic profile, and social media posts.

Airports are a bit of a special case, however. As walled gardens, airport security can leverage the benefits of vertical integration. And as gateways to faraway destinations, travelers are forced to either sign-away certain rights or take the bus. Most d spaces aren't like this. From small businesses to the public park, our daily security largely depends on the goodwill and discretion of other people. Thus, to the extent AI creates security and privacy risks _everywhere_, more and more d spaces may end up operating like an airport, i.e. like a surveillance state in miniature.

In turn, the coming [intelligence explosion](https://www.dwarkeshpatel.com/p/carl-shulman#details) puts liberal democracy on a knife edge. On one side is an AI Leviathan; a global singleton that restores order through a Chinese-style panopticon and social credit system. On the other is state collapse and political fragmentation, as our legacy institutions fail to adapt and give way to new, [AI-native organizations](https://blog.mutable.ai/p/the-ai-organization-part-i) that solve the [principal-agent problem](https://en.wikipedia.org/wiki/Principal%E2%80%93agent_problem) and unlock localized collective action at blazing speeds. This includes the fortification of privacy and security, obtained in part through an opt-in covenant to leave one’s bioweapons and x-ray glasses at the proverbial door.

Peering through the event horizon of this latter path, the contours of a new, quasi-medieval social order begin to take shape. But I’m running up against Substack’s character limit, so that will have to wait for [Part II](https://www.secondbest.ca/p/ai-and-leviathan-part-ii).

**In the meantime, enjoy this podcast I recorded with Erik Torenberg:**
