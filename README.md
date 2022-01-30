# git-ssh-keys-keeper
manager multi git ssh keys in one machine, with serval private or public repo.

```bash
pip install git-ssh-key
```

change git url

```bash
$git-ssh-key https://github.com/alingse/git-ssh-key.git
New repo address: git@github.com-f5851eb:alingse/git-ssh-key.git
New repo public rsa key: /Users/alingse/.ssh/github.com-f5851eb.id_rsa.pub
```

## Dev

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

## TODO

1. show public key ?
2. better -c -k ?
3. more error checking raise click.ClickException
4. os.system need
5. add more test ?
