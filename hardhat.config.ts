import '@nomiclabs/hardhat-ethers';
import '@nomiclabs/hardhat-vyper';
import '@typechain/hardhat';
import 'hardhat-abi-exporter';
import type { HardhatUserConfig } from 'hardhat/config';

const config: HardhatUserConfig = {
	vyper: {
		version: '0.3.1'
	},
	abiExporter: {
		path: './abis',
		runOnCompile: true,
		clear: true,
		flat: true,
		only: ['VotingEscrow']
	},
	typechain: {
		outDir: 'typechain',
		target: 'ethers-v5',
		alwaysGenerateOverloads: false,
		externalArtifacts: ['abis/*.json']
	}
};

export default config;
