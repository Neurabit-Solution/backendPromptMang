# 📱 Google AdMob Integration Guide

This guide explains how to set up Rewarded Ads in MagicPic and award users **1 credit per ad watch**.

## 1. AdMob Dashboard Setup

1.  **Create an AdMob Account**: Go to [apps.admob.com](https://apps.admob.com/).
2.  **Add App**: 
    *   Click **Apps** in the sidebar → **Add App**.
    *   Register your Android or iOS app.
3.  **Create Ad Unit**:
    *   Select your app from the sidebar.
    *   Click **Ad units** → **Add ad unit**.
    *   Select **Rewarded Ad**.
    *   **Reward settings**:
        *   Set **Reward amount** to `1`.
        *   Set **Reward item** to `Credit`.
4.  **How to Collect Your IDs**:
    *   **App ID**: Go to **App Settings** in the sidebar. Look for "App ID" (Format: `ca-app-pub-xxxxxxxxxxxxxxxx~yyyyyyyyyy`).
    *   **Ad Unit ID**: Go to **Ad units** in the sidebar. Copy the ID for your rewarded ad (Format: `ca-app-pub-xxxxxxxxxxxxxxxx/zzzzzzzzzz`).

---

## 2. Backend Configuration

Add the following keys to your `config.properties` file in the root directory to control the reward logic:

```ini
# --- AdMob Rewards ---
# Credits awarded per ad watch
rewarded_ad_credits=1
# Maximum rewarded ads a user can watch per day
daily_ad_watch_limit=5
```

These values are automatically picked up by the backend to enforce limits and award the correct amount.

---

## 3. Frontend & App Implementation

### A. Mobile App Configuration
Before using the SDK, you must add your **App ID** to your mobile project:

*   **Android**: Add to `AndroidManifest.xml` inside `<application>`:
    ```xml
    <meta-data
        android:name="com.google.android.gms.ads.APPLICATION_ID"
        android:value="ca-app-pub-xxxxxxxxxxxxxxxx~yyyyyyyyyy"/>
    ```
*   **iOS**: Add to `Info.plist`:
    ```xml
    <key>GADApplicationIdentifier</key>
    <string>ca-app-pub-xxxxxxxxxxxxxxxx~yyyyyyyyyy</string>
    ```

### B. Load the Ad (React Native Example)
Load the ad unit using the **Ad Unit ID** collected earlier.

```javascript
import { RewardedAd, RewardedAdEventType, TestIds } from 'react-native-google-mobile-ads';

// Use TestIds.REWARDED during development to avoid policy violations!
const adUnitId = __DEV__ ? TestIds.REWARDED : 'ca-app-pub-xxxxxxxxxxxxxxxx/zzzzzzzzzz';

const rewardedAd = RewardedAd.createForAdUnit(adUnitId, {
  requestNonPersonalizedAdsOnly: true,
});
```

### C. Handle the Reward
When the user finishes watching, the SDK triggers the `EARNED_REWARD` event. **This is when you notify the backend.**

```javascript
rewardedAd.addAdEventListener(RewardedAdEventType.EARNED_REWARD, (reward) => {
  console.log('User earned reward:', reward);
  
  // Call MagicPic Backend to add the credit
  awardCreditOnBackend();
});
```

### D. Backend API Call
The frontend must send a POST request with the user's Auth Token.

```javascript
const awardCreditOnBackend = async () => {
  try {
    const response = await fetch('https://api.magicpic.com/api/rewards/admob', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userAccessToken}`
      },
      body: JSON.stringify({
        ad_unit_id: "rewarded_ad_main", // The name or ID you use to track this unit
        platform: "android"
      })
    });
    
    const result = await response.json();
    if (result.success) {
      alert(`Success! Your new balance is ${result.data.new_balance} credits.`);
    }
  } catch (error) {
    console.error("Failed to reward user:", error);
  }
};
```

---

## 4. Backend Logic (Already Implemented)

The backend endpoint `/api/rewards/admob` handles the following automatically:
*   **Daily Limits**: Checks `daily_ad_watch_limit` from config.
*   **Audit Log**: Saves every ad watch in the `ad_watches` table.
*   **Transaction History**: Updates `credit_transactions`.
*   **Balance Update**: Directly increments user credits in the database.

---

## 5. Enhanced Security (Optional)

For production, it is highly recommended to enable **Server-Side Verification (SSV)** in the AdMob dashboard.
1.  In AdMob: Go to Ad Unit settings → Advanced settings → **Server-side verification**.
2.  Enter Callback URL: `https://api.magicpic.com/api/rewards/admob-ssv`.
3.  This makes the system 100% secure by verifying Google's digital signature.

*Note: If you need the SSV backend implementation, please ask!*
