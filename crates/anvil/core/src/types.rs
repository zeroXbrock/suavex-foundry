use alloy_primitives::{Address, Bytes, TxHash, B256, U128, U256, U64};
use alloy_rpc_types::{other::OtherFields, AccessListItem, Signature};
use revm::primitives::SpecId;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

#[cfg(feature = "serde")]
use serde::{de::Error, Deserializer, Serializer};

/// Represents the params to set forking which can take various forms
///  - untagged
///  - tagged `forking`
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Forking {
    pub json_rpc_url: Option<String>,
    pub block_number: Option<u64>,
}

#[cfg(feature = "serde")]
impl<'de> serde::Deserialize<'de> for Forking {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        #[derive(serde::Deserialize)]
        #[serde(rename_all = "camelCase")]
        struct ForkOpts {
            pub json_rpc_url: Option<String>,
            #[serde(
                default,
                deserialize_with = "crate::eth::serde_helpers::numeric::deserialize_stringified_u64_opt"
            )]
            pub block_number: Option<u64>,
        }

        #[derive(serde::Deserialize)]
        struct Tagged {
            forking: ForkOpts,
        }
        #[derive(serde::Deserialize)]
        #[serde(untagged)]
        enum ForkingVariants {
            Tagged(Tagged),
            Fork(ForkOpts),
        }
        let f = match ForkingVariants::deserialize(deserializer)? {
            ForkingVariants::Fork(ForkOpts { json_rpc_url, block_number }) => {
                Forking { json_rpc_url, block_number }
            }
            ForkingVariants::Tagged(f) => Forking {
                json_rpc_url: f.forking.json_rpc_url,
                block_number: f.forking.block_number,
            },
        };
        Ok(f)
    }
}

/// Additional `evm_mine` options
#[derive(Clone, Debug, PartialEq, Eq)]
#[cfg_attr(feature = "serde", derive(serde::Deserialize))]
#[cfg_attr(feature = "serde", serde(untagged))]
pub enum EvmMineOptions {
    Options {
        #[cfg_attr(
            feature = "serde",
            serde(
                deserialize_with = "crate::eth::serde_helpers::numeric::deserialize_stringified_u64_opt"
            )
        )]
        timestamp: Option<u64>,
        // If `blocks` is given, it will mine exactly blocks number of blocks, regardless of any
        // other blocks mined or reverted during it's operation
        blocks: Option<u64>,
    },
    /// The timestamp the block should be mined with
    #[cfg_attr(
        feature = "serde",
        serde(
            deserialize_with = "crate::eth::serde_helpers::numeric::deserialize_stringified_u64_opt"
        )
    )]
    Timestamp(Option<u64>),
}

impl Default for EvmMineOptions {
    fn default() -> Self {
        EvmMineOptions::Options { timestamp: None, blocks: None }
    }
}

/// Represents the result of `eth_getWork`
/// This may or may not include the block number
#[derive(Debug, Default, PartialEq, Eq)]
pub struct Work {
    pub pow_hash: B256,
    pub seed_hash: B256,
    pub target: B256,
    pub number: Option<u64>,
}

#[cfg(feature = "serde")]
impl serde::Serialize for Work {
    fn serialize<S>(&self, s: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        if let Some(num) = self.number {
            (&self.pow_hash, &self.seed_hash, &self.target, U256::from(num)).serialize(s)
        } else {
            (&self.pow_hash, &self.seed_hash, &self.target).serialize(s)
        }
    }
}

/// A hex encoded or decimal index
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct Index(usize);

impl From<Index> for usize {
    fn from(idx: Index) -> Self {
        idx.0
    }
}

#[cfg(feature = "serde")]
impl<'a> serde::Deserialize<'a> for Index {
    fn deserialize<D>(deserializer: D) -> Result<Index, D::Error>
    where
        D: serde::Deserializer<'a>,
    {
        use std::fmt;

        struct IndexVisitor;

        impl<'a> serde::de::Visitor<'a> for IndexVisitor {
            type Value = Index;

            fn expecting(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
                write!(formatter, "hex-encoded or decimal index")
            }

            fn visit_u64<E>(self, value: u64) -> Result<Self::Value, E>
            where
                E: Error,
            {
                Ok(Index(value as usize))
            }

            fn visit_str<E>(self, value: &str) -> Result<Self::Value, E>
            where
                E: Error,
            {
                if let Some(val) = value.strip_prefix("0x") {
                    usize::from_str_radix(val, 16).map(Index).map_err(|e| {
                        Error::custom(format!("Failed to parse hex encoded index value: {e}"))
                    })
                } else {
                    value
                        .parse::<usize>()
                        .map(Index)
                        .map_err(|e| Error::custom(format!("Failed to parse numeric index: {e}")))
                }
            }

            fn visit_string<E>(self, value: String) -> Result<Self::Value, E>
            where
                E: Error,
            {
                self.visit_str(value.as_ref())
            }
        }

        deserializer.deserialize_any(IndexVisitor)
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
#[cfg_attr(feature = "serde", derive(serde::Serialize, serde::Deserialize))]
#[cfg_attr(feature = "serde", serde(rename_all = "camelCase"))]
pub struct NodeInfo {
    pub current_block_number: U64,
    pub current_block_timestamp: u64,
    pub current_block_hash: B256,
    pub hard_fork: SpecId,
    pub transaction_order: String,
    pub environment: NodeEnvironment,
    pub fork_config: NodeForkConfig,
}

#[derive(Clone, Debug, PartialEq, Eq)]
#[cfg_attr(feature = "serde", derive(serde::Serialize, serde::Deserialize))]
#[cfg_attr(feature = "serde", serde(rename_all = "camelCase"))]
pub struct NodeEnvironment {
    pub base_fee: U256,
    pub chain_id: u64,
    pub gas_limit: U256,
    pub gas_price: U256,
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
#[cfg_attr(feature = "serde", derive(serde::Serialize, serde::Deserialize))]
#[cfg_attr(feature = "serde", serde(rename_all = "camelCase"))]
pub struct NodeForkConfig {
    pub fork_url: Option<String>,
    pub fork_block_number: Option<u64>,
    pub fork_retry_backoff: Option<u128>,
}

/// Anvil equivalent of `hardhat_metadata`.
/// Metadata about the current Anvil instance.
/// See <https://hardhat.org/hardhat-network/docs/reference#hardhat_metadata>
#[derive(Clone, Debug, PartialEq, Eq)]
#[cfg_attr(feature = "serde", derive(serde::Serialize, serde::Deserialize))]
#[cfg_attr(feature = "serde", serde(rename_all = "camelCase"))]
pub struct AnvilMetadata {
    pub client_version: &'static str,
    pub chain_id: u64,
    pub instance_id: B256,
    pub latest_block_number: u64,
    pub latest_block_hash: B256,
    pub forked_network: Option<ForkedNetwork>,
    pub snapshots: BTreeMap<U256, (u64, B256)>,
}

/// Information about the forked network.
/// See <https://hardhat.org/hardhat-network/docs/reference#hardhat_metadata>
#[derive(Clone, Debug, PartialEq, Eq)]
#[cfg_attr(feature = "serde", derive(serde::Serialize, serde::Deserialize))]
#[cfg_attr(feature = "serde", serde(rename_all = "camelCase"))]
pub struct ForkedNetwork {
    pub chain_id: u64,
    pub fork_block_number: u64,
    pub fork_block_hash: TxHash,
}

/// Transaction object used in RPC (should be in alloy_rpc)
#[derive(Debug, Default, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TransactionSuave {
    /// Hash
    pub hash: B256,
    /// Nonce
    pub nonce: U64,
    /// Block hash
    pub block_hash: Option<B256>,
    /// Block number
    pub block_number: Option<U256>,
    /// Transaction Index
    pub transaction_index: Option<U256>,
    /// Sender
    pub from: Option<Address>,
    /// Recipient
    pub to: Option<Address>,
    /// Transferred value
    pub value: U256,
    /// Gas Price
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gas_price: Option<U128>,
    /// Gas amount
    pub gas: U256,
    /// Max BaseFeePerGas the user is willing to pay.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_fee_per_gas: Option<U128>,
    /// The miner's tip.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_priority_fee_per_gas: Option<U128>,
    /// Configured max fee per blob gas for eip-4844 transactions
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_fee_per_blob_gas: Option<U128>,
    /// Data
    pub input: Bytes,
    /// All _flattened_ fields of the transaction signature.
    ///
    /// Note: this is an option so special transaction types without a signature (e.g. <https://github.com/ethereum-optimism/optimism/blob/0bf643c4147b43cd6f25a759d331ef3a2a61a2a3/specs/deposits.md#the-deposited-transaction-type>) can be supported.
    #[serde(flatten, skip_serializing_if = "Option::is_none")]
    pub signature: Option<Signature>,
    /// The chain id of the transaction, if any.
    pub chain_id: Option<U64>,
    /// Contains the blob hashes for eip-4844 transactions.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub blob_versioned_hashes: Vec<B256>,
    /// EIP2930
    ///
    /// Pre-pay to warm storage access.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub access_list: Option<Vec<AccessListItem>>,
    /// EIP2718
    ///
    /// Transaction type, Some(2) for EIP-1559 transaction,
    /// Some(1) for AccessList transaction, None for Legacy
    #[serde(rename = "type", skip_serializing_if = "Option::is_none")]
    pub transaction_type: Option<U64>,

    /// Arbitrary extra fields.
    ///
    /// This captures fields that are not native to ethereum but included in ethereum adjacent networks, for example fields the [optimism `eth_getTransactionByHash` request](https://docs.alchemy.com/alchemy/apis/optimism/eth-gettransactionbyhash) returns additional fields that this type will capture
    #[serde(flatten)]
    pub other: OtherFields,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn serde_forking() {
        let s = r#"{"forking": {"jsonRpcUrl": "https://ethereumpublicnode.com",
        "blockNumber": "18441649"
      }
    }"#;
        let f: Forking = serde_json::from_str(s).unwrap();
        assert_eq!(
            f,
            Forking {
                json_rpc_url: Some("https://ethereumpublicnode.com".into()),
                block_number: Some(18441649)
            }
        );
    }
}
