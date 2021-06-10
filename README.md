## Profiles Catalogue Dataset

This repository contains the content of, and scripts for loading, the [W3ID Profiles Catalogue](https://profiles.conneg.info).


## Profile Guidelines
Each of the profiles in this catalogue are described using the [Profiles Vocabulary (PROF)](https://www.w3.org/TR/dx-prof/). For this system this means that each profile has a main profile asset which is an [RDF](https://www.w3.org/RDF/) file in the (Turtle)[https://www.w3.org/TR/turtle/] format, called *profile.ttl* within a folder which may contain a few other files.

So, each profile must look like this:

*  `PROFILE_FOLDER`
    * `PROFILE_FILE.ttl`
    * *other profile file x*
    * *other profile file y*

The actual name of `PROFILE_FOLDER` & `PROFILE_FILE` is based on the profile's ID, as assigned by ProfCat (i.e. it's not something the profile sets), but it's usually obvious what it is - the profile acronym or last segment of its URI. It's only used to separate profile content for management - but should be reconisable as a short code for the profile. 





## License
The functioning of this catalogue - scripts, API etc. - are licensed for use using the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) (see the deed [LICENSE file](LICENSE) for details).


## Developer contact
If you want to be in contact with the developers outside the GitHub or SURROUND contact channels please use these details:

**Lead Developer**  
Dr Nicholas Car  
_Data Systems Architect_  
<nicholas.car@surroundaustralia.com>  
github: nicholascar  
