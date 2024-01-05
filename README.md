# Offering Two-Way Privacy for Evolved Purchase Inquiries

## About
This repository contains our prototypes for protocols (PPI, HPI, and cHPI) to offer privacy-preserving price and availability comparison for purchase inquires.

> Dynamic and flexible business relationships are expected to become more important in the future to accommodate specialized change requests or small-batch production. Today, buyers and sellers must disclose sensitive information on products upfront before the actual manufacturing. However, without a trust relation, this situation is precarious for the involved companies as they fear for their competitiveness. Related work overlooks this issue so far: Existing approaches only protect the information of a single party only, hindering dynamic and on-demand business relationships. To account for the corresponding research gap of inadequately privacy-protected information and to deal with companies without an established trust relation, we pursue the direction of innovative privacy-preserving purchase inquiries that seamlessly integrate into today's established supplier management and procurement processes. Utilizing well-established building blocks from private computing, such as private set intersection and homomorphic encryption, we propose two designs with slightly different privacy and performance implications to securely realize purchase inquiries over the Internet. In particular, we allow buyers to consider more potential sellers without sharing sensitive information and relieve sellers of the burden of repeatedly preparing elaborate yet discarded offers. We demonstrate our approaches' scalability using two real-world use cases from the domain of production technology. Overall, we present deployable designs that offer two-way privacy for purchase inquiries and, in turn, fill a gap that currently hinders establishing dynamic and flexible business relationships. In the future, we expect significantly increasing research activity in this overlooked area to address the needs of an evolving production landscape.

## Publication

- Jan Pennekamp, Markus Dahlmanns, Frederik Fuhrmann, Timo Heutmann, Alexander Kreppein, Dennis Grunert, Christoph Lange, Robert H. Schmitt, and Klaus Wehrle: *Offering Two-Way Privacy for Evolved Purchase Inquiries*. ACM Transactions on Internet Technology, 23(4), ACM, 2023.

If you use any portion of our work, please cite our publication.

```bibtex
@inproceedings{pennekamp2023offering,
    author = {Pennekamp, Jan and Dahlmanns, Markus and Fuhrmann, Frederik and Heutmann, Timo and Kreppein, Alexander and Grunert, Dennis and Lange, Christoph and Schmitt, Robert H. and Wehrle, Klaus},
    title = {{Offering Two-Way Privacy for Evolved Purchase Inquiries}},
    journal = {ACM Transactions on Internet Technology},
    year = {2023},
    volume = {23},
    number = {4},
    publisher = {ACM},
    month = {11},
    doi = {10.1145/3599968},
    issn = {1533-5399},
}
```

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.

If you are planning to integrate parts of our work into a commercial product and do not want to disclose your source code, please contact us for other licensing options via email at pennekamp (at) comsys (dot) rwth-aachen (dot) de

## Acknowledgments

Funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) under Germany's Excellence Strategy – EXC-2023 Internet of Production – 390621612.

---

## Introduction

Each protocol runs separately in a set of docker containers.
Please refer to our paper for an in-depth presentation of each protocol.
We provide a `docker-compose.yml` for each protocol that creates all required containers for the respective protocol.

### Setup

All protocols run in docker containers.
* Install [docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/).
* Navigate to the `celery-docker` folder for the respective protocol with `$ cd <PROTOCOL>/celery-docker`.
 *Replace `<PROTOCOL>` by the respective protocol, i.e., PPI, HPI, or cHPI.*
* Build all required containers with `$ docker-compose build`.
* Start the protocol with `$ docker-compose up`.
  **WARNING:** *Note that this will automatically start the real-world evaluation. To start all containers for the protocol without evaluation, remove the `evaluation` container from the `docker-composer.yml` file in the `celery-docker` directory*

## Library Versions

For our prototypes, we utilize the following protocols:
* PyPSI: A private set intersection library **[PPI]**
  *Please note that the library was previously available on [GitHub](https://github.com/OpenMined). We ship the sources in `PPI/celery-docker/app/PyPSI/`.*
* [Order Revealing Encryption](https://github.com/kpatsakis/OrderRevealingEncryption) in Python **[PPI]**
* [python-paillier](https://github.com/data61/python-paillier) **[HPI & cHPI]**

We include all libraries in our repository as we made minor adjustments to the original source code.
Thus, no additional setup steps are needed.

In the following, we report on the made changes:
* PyPSI:
  - `bloom_filter.py`:
  	- l. 128ff.: add (de)serialization support
* Order Revealing Encryption:
  - `ore.py`:
  	- l. 20: add support for Python3
  	- l. 31ff.: extend comparison to also support inputs of unequal length
* python-paillier:
  - `paillier.py`
  	- l.97: increase maximum value that may be stored

## System Requirements

We do not require any specific hardware or software.
In general, our design is detached from the specific hardware and can be configured accordingly.
For our measurements, we noticed a maximum memory consumption of 3 GB.
In a real-world deployment, the different entities would run on different devices and, thus, require less memory on a single machine.

## Configuration

All input is created in the `<PROTOCOL>/celery-docker/app/create_values.py` file for the respective protocol. As our protocols are independent of the underlying domain, the input creation requires only the size (configuration size for buyer, catalog size for seller) as input.
To manually construct a use case, create the corresponding files containing the seller's input in `<PROTOCOL>/celery-docker/app/Seller` and files for the buyer's input in `<PROTOCOL>/celery-docker/app/Buyer` according to the format of the files created in `<PROTOCOL>/celery-docker/app/create_values.py`

### Real-World Input Data

As our approaches are oblivious of the processed/compared input data, and they only rely on general ids.
Thus, for our general performance evaluation, we operate on randomly-generated input data.
Our real-world evaluation is based on machine tool data, which we will include in this repository when publicly sharing this artifact on GitHub.
The protocol runtime and conducted operations are independent of the processed products -- only the input dimensions are relevant.
Thus, the original, real-world input data is not required when verifying the reported performance (regardless of the specific setting).

### Evaluation Parameters

To adjust the evaluation parameters, specify the catalog sizes to be evaluated by adjusting the `max_nums` list in `<PROTOCOL>/celery-docker/app/create_values.py` and the number of items in the buyer's config by adjusting the `configs` list in `<PROTOCOL>/celery-docker/app/create_values.py`.
All seller prices are random numbers between 2 and 2**32.
Alternative, to alter the prices, adjust the price creation in `create_seller_prices()` in `<PROTOCOL>/celery-docker/app/create_values.py`.

### HPI/cHPI Specifics

Next, we present these input files for the HPI/cHPI protocol in more detail.
* A file `config.txt` in `<PROTOCOL>/celery-docker/app/Buyer/` containing one entry per line for the size of the product catalog '1\n' if item is required, '0\n' else.
* A file `threshold.txt` in `<PROTOCOL>/celery-docker/app/Buyer/` containing the price threshold 'price\n'
* A file `prices.txt` in `<PROTOCOL>/celery-docker/app/Seller/` containing the price for each entry in the catalog or 'MAXVALUE' if item is not avaialble as 'price\n'

## Evaluation

To repeat our performance measurements (as included in the paper) that demonstrate the scalability aspects of our approaches, the `create_values.py` files must be configured with the following settings:
`max_nums = [5000, 10000, 50000, 100000, 500000, 1000000]` and `configs = [10]`.
*Please note that the provided software artifact runs our real-world performance measurements by default.*

To recreate the runs concerning our real-world use cases, i.e., our real-world performance measurements, the following settings should be configured:
`max_nums = [38880, 944784]` and `configs = [1]`.

The respective lines are already prepared, i.e., simply (un)commenting the respective lines is sufficient.
Alternatively, any arbitrary setting can be configured by modifying these two parameters (as described above).

The variable `number_of_runs` in `<PROTOCOL>/celery-docker/app/create_values.py` configures the number of (identical) evaluation.
We fix it with `10` by default.
To demonstrate the proof of concept of our implementation, the number can be reduced to (linearly) speedup the overall evaluation runtime.

To run the (real-world) evaluation simply start the unmodified docker-compose file for the selected protocol by executing:
* `$ cd <PROTOCOL>/celery-docker/app/Buyer/`
* `$ docker-compose up`
