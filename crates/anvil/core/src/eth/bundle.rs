use alloy_primitives::{Bytes, B256, U256};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Default, Eq, PartialEq, Serialize, Deserialize)]
#[serde(default, rename_all = "camelCase")]
pub struct SBundle {
    pub block_number: Option<U256>, // // if BlockNumber is set it must match DecryptionCondition
    pub max_block: Option<U256>,
    #[serde(rename = "txs")]
    pub transactions: Vec<Bytes>,
    pub reverting_hashes: Option<Vec<B256>>,
}
