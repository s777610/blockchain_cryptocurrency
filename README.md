# blockchain_cryptocurrency

This project is one of the use cases of block-chain.
I build the small cryptocurrency system with python.

1. The system allows users to create wallets.
2. The key pair(public key and private key) is generated when creating the wallet.
2. After creating the wallet, users can start mining the new block in order to get the reward.
3. After getting rewards, users can send cryptocurrency to other users by assigning a public key of the recipient.
4. All transactions data will be stored in open transactions temporarily, which is a list of transactions.
5. The meaning of mining is doing "proof of work".
6. Proof of work, which is a processing of guessing the number proof. The users have to hash the combination of open transactions, the hash of previous block and proof. After that, the hashed result must start with "00". The level of difficulty is adjustable.
6. After mining a new block, the data of open transactions is stored in the new block, and open transactions will be an empty list.
7. All node can make HTTP requests to their peer nodes in order to share their data.
8. Majority of the process includes different verifications in order to make sure the system is secure.

## Installation (platform: osx-64)
1. Create conda env
```
conda create -n <env_name>
```
2. Activate env
```
source activate <env_name>
```
3. Install package from requirements
```
conda install --yes --file requirements.txt
```

## Here is my home page
<img width="792" alt="screen shot 2018-09-08 at 10 45 08 pm" src="https://user-images.githubusercontent.com/35472776/45261552-73081a80-b3ba-11e8-971e-3441d1a74830.png">

## After creating a wallet, users can starting mining.
<img width="1018" alt="screen shot 2018-09-08 at 10 51 53 pm" src="https://user-images.githubusercontent.com/35472776/45261571-1eb16a80-b3bb-11e8-84f5-22ba4c16b46a.png">

## Users are able to check every transaction and block in the blockchain
<img width="1030" alt="screen shot 2018-09-08 at 10 52 10 pm" src="https://user-images.githubusercontent.com/35472776/45261579-3daffc80-b3bb-11e8-8596-930df40046ba.png">

## Users are able to check every open transaction.
<img width="1008" alt="screen shot 2018-09-08 at 10 52 39 pm" src="https://user-images.githubusercontent.com/35472776/45261583-443e7400-b3bb-11e8-9b97-6d7cc7191fa6.png">
