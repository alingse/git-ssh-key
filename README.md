# git-ssh-key

manager multi git repo ssh keys in one machine, with multi private or public repo.

this command will auto generate the key and add it to your ssh config

## usage

```bash
pip install git-ssh-key
```

run command with your repo link

```bash
git-ssh-key https://github.com/alingse/git-ssh-key.git
```

it will print the new alias repo link and the new public key,

```bash
New repo address: git@github.com-f5851eb:alingse/git-ssh-key.git
New repo public rsa key: /Users/alingse/.ssh/github.com-f5851eb.id_rsa.pub
```

you can add it to repo's setting keys

```bash
git-ssh-key --help

git-ssh-key --config your.ssh.config --keys your-ssh-keys/ your.repo
```

## How

I ever see some stackoverflow and github gist, and just make them a tool


## Develop

```bash
pdm install

pdm build
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
2. better -c -k ?
3. more error checking raise click.ClickException
4. replace os.system
5. add more test ?
6. support duplicate keys ?
7. better giturlparse
8. allow user generate the key first

