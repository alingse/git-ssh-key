# git-ssh-key

manager multi git repo ssh keys in one machine, with multi private or public repo.

this command will auto generate the key and add it to your ssh config

## usage

```bash
pip install git-ssh-key
```

run command with your repo link like

```bash
git-ssh-key https://github.com/alingse/git-ssh-key.git
```

it will print the new alias repo link and the new public key,
```bash
New repo address: git@github.com-f5851eb:alingse/git-ssh-key.git
New repo public rsa key: /Users/alingse/.ssh/github.com-f5851eb.id_rsa.pub
```

the public key has already been configured in your ssh config file, remember add it to repo's setting keys (https://github.com/user/repo/settings/keys)

and then just clone like this

```bash
git clone git@github.com-f5851eb:alingse/git-ssh-key.git
```

more options see

```bash
git-ssh-key --help
```


```bash
git-ssh-key -c git.ssh.config --keys ./../ -t web-backend git@github.com:alingse/git-ssh-key.git
```


## How it work

I ever see some stackoverflow and github gist, and just make them a tool

`git-ssh-key` will read `.ssh/config` (default) and write into an alias host config.

like this

```
Host github.com-f5851eb
HostName github.com
User git
IdentityFile /Users/alingse/.ssh/github.com-f5851eb.id_rsa
```

the `f5851eb` is tag, default generate by hash(url)

## Develop

pdm see https://pdm.fming.dev/

```bash
pdm install

pdm build

pdm run git-ssh-key --help
```

### publish

add once

```bash
pdm config publish.username xxx
pdm config publish.password yyy
```

```bash
pdm publish
```

## more TODO

1. show public key ?
5. add more test ?
7. better giturlparse
