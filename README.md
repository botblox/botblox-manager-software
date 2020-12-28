<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Thanks again! Now go create something AMAZING! :D
***
***
***
*** To avoid retyping too much info. Do a search and replace for the following:
*** github_username, repo_name, twitter_handle, email, project_title, project_description
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]


<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://www.botblox.io/">
    <img src="images/logo.png" alt="Logo" width="160" height="160">
  </a>

  <h3 align="center">BotBlox software</h3>

  <p align="center">
    Software created by BotBlox to configure settings on our products
    <br />
    <a href="https://botblox.atlassian.net/wiki/spaces/HARDWARE/overview"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://botblox.atlassian.net/wiki/spaces/HARDWARE/overview">View Demo</a>
    ·
    <a href="https://github.com/botblox/botblox-manager-software/issues">Report Bug</a>
    ·
    <a href="https://github.com/botblox/botblox-manager-software/issues">Request Feature</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#installation">Installation</a>
      <ul>
        <li><a href="#getting-started">Getting Started</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## About The Project

Welcome to BotBlox Software. We designed this software to go along with our [firmware](https://github.com/botblox/botblox-manager-firmware) to allow our community of customers and developers to manually configure custom settings on BotBlox products, such as the SwitchBlox: our flagship Etheret switch. For a while now, our customers have requested that they want to be able to program VLAN membership, Quality-of-service, Port mirroring, etc on our products. This Software contains a containerized CLI application, written in Python 3.8, that will allow you to configure the SwitchBlox to perform certain managed functions in your application. The CLI runs in a docker container, allowing us to bundle the dependencies of the application with the application source code itself, without having to worry about host OS. This application was designed with developers in mind, we wanted to make developing features for this application as simple as possible. We very much encourage people to point out improvements, bugs or missing features they want implemented as we want to be very responsive to the needs of the developer and customer.   


### Built With

* [Docker](https://www.docker.com/)
* [VirtualBox](https://www.virtualbox.org/)
* [PySerial](https://github.com/pyserial/pyserial)

<!-- Installation -->
## Installation

You'll need to install software that allows the running of containerized applications, with permission to access a USB device (in this case, a USB-to-UART converter).

#### Linux
* Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop) (called 'Docker') for your given Linux distribution (or however you wish to use Docker, I used Docker Desktop so I politely suggest you download/install that too).

#### MacOS or Windows
* Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop) (called 'Docker') for your given Linux distribution (or however you wish to use Docker, I used Docker Desktop so I politely suggest you download/install that too).
* Download and install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) and download and install [VirtualBox Extension Pack](https://www.virtualbox.org/wiki/Downloads) if your device has USB 2.0 ports.

### Getting Started

#### Linux

To get a local copy up and running follow these simple steps.
1. Clone this repo in the directory 
```sh
   git clone https://github.com/botblox/botblox-manager-software.git
```
2. `cd` to project directory
```sh
    cd /path/to/project/dir
```
3. To run the code, we have to build the container image
```sh
    docker build -t switchblox-manager .
```
4. Run the image with access to the port connected to the USB-to-UART converter device
```sh
    docker run --rm -it --device=/device/name/on/system:/dev/ttyUSB0/ switchblox-manager 
```
5. Inside the shell running in the container image, run any CLI commands to write serial data that will write to the USB-to-USART device port
```sh
    python app.py --help
```

#### MacOS and Windows
To get a local copy up and running follow these simple steps.
1. Clone this repo in the directory 
```sh
   git clone https://github.com/botblox/botblox-manager-software.git
```
2. `cd` to project directory
```sh
    cd /path/to/project/dir
```

_Important Note_

It is not trivial to grant device access to the Docker Daemon when running on MacOS or Windows as the Host OS as the Docker Daemon only runs natively on Linux, which means that the Docker Daemon runs inside of a VM (`hyperkit` for MacOS and `Microsoft Hyper-V`) when being used on MacOS or Windows. Unfortunately, both VMs do not support USB forwarding so it is impossible to allow the container access to the USB-to-UART converter device port. However, this can be circumvented by instead running the docker daemon inside of a VM that we run inside VirtualBox and simply point the docker client so that it sends API requests to the docker daemon running that custom VM. We can ensure that this VM has USB device filtering enabled, thus granting the container access. 

3. (One time) Create the VM which will run the `docker daemon` inside and name it `default`
```sh
    docker-machine create -d virtualbox default
```
4. (One time) Stop the machine so we can configure it
```sh
    docker-machine stop
```

Do either Steps 5. or 6. before moving to 7.

5a. (One time) You can configure the VM in VirtualBox desktop application.
5b. Open `VirtualBox` application and locate `default` VM.
5c. Go to `Settings`.
5d. Go to `Ports`.
5e. Check `Enable USB Controller` on.
5f. Open the 'Add USB Device Filter' icon and select the USB-to-UART converter device
5g. Click `Ok`
5h. Back in the terminall shell inside the project directory, run 
```sh
    docker-machine start
```
6a. Enable USB filtering in VM running docker daemon (if you have VirtualBox extension pack installed)
```sh
    vboxmanage modifyvm default --usbehci on
```
6b. Else if VirtualBox extension is not install
```sh
    vboxmanage modifyvm default --usb on
```
6c. Add the USB device filter to the `default` VM assuming you know the USB-to-UART device name, vendor id and product id.
For example, my personal setup uses.
```sh
    vboxmanage usbfilter add 0 --target default --name 'FTDI FT232R USB UART' --vendorid 0x0403 --productid 0x6001
```
7. Export the environment variables used to tell Docker Client to use the new VM to send API requests to the docker daemon, instead of native mode. 
```sh
    eval $(docker-machine env default)
```
Note: this will only export environment variables locally in the shell, if you want to set user system environment variables, add them to `~/.bash_profile`
8. To run the code, we have to build the container image
```sh
    docker build -t switchblox-manager .
```
9. Run the image with access to the port connected to the USB-to-UART converter device
```sh
    docker run --rm -it --device=/dev/ttyUSB0/ switchblox-manager 
```
10. Inside the shell running in the container image, run any CLI commands to write serial data that will write to the USB-to-USART device port
```sh
    python app.py --help
```

<!-- USAGE EXAMPLES -->
## Usage

Use this space to see useful examples of how this project can be used. Additional screenshots, code examples and demos may be added in this space as necessary. Link to full resouces below.

_For more examples, please refer to the [Documentation](https://botblox.atlassian.net/wiki/spaces/HARDWARE/overview)_


<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/botblox/botblox-manager-software/issues) for a list of proposed features (and known issues).


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
2. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
3. Push to the Branch (`git push origin feature/AmazingFeature`)
4. Open a Pull Request

Please also note the [Developer Guidelines](https://botblox.atlassian.net/wiki/spaces/HARDWARE/overview) that BotBlox kindly asks of all those who are generous enough to devote their time using or developing on this product.


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<!-- CONTACT -->
## Contact

Project Link: [https://github.com/botblox/botblox-manager-software](https://github.com/botblox/botblox-manager-software)


<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
* [Christopher McClellan](https://dev.to/rubberduck/using-usb-with-docker-for-mac-3fdd)
* [Milad Alizadeh](https://mil.ad/docker/2018/05/06/access-usb-devices-in-container-in-mac.html)

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors-anon/botblox/botblox-manager-software?style=for-the-badge
[contributors-url]: https://github.com/botblox/botblox-manager-software/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/botblox/botblox-manager-software?style=for-the-badge
[forks-url]: https://github.com/botblox/botblox-manager-software/network/members
[stars-shield]: https://img.shields.io/github/stars/botblox/botblox-manager-software?style=for-the-badge
[stars-url]: https://github.com/botblox/botblox-manager-software/stargazers
[issues-shield]: https://img.shields.io/github/issues/botblox/botblox-manager-software?style=for-the-badge
[issues-url]: https://github.com/botblox/botblox-manager-software/issues
[license-shield]: https://img.shields.io/github/license/botblox/botblox-manager-software?style=for-the-badge
[license-url]: https://github.com/botblox/botblox-manager-software/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/company/botblox/

