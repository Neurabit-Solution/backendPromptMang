# 📱 Google AdMob Integration Guide

This guide explains how to set up Rewarded Ads in MagicPic and award users **1 credit per ad watch**.

## 1. AdMob Dashboard Setup

1.  **Create an AdMob Account**: Go to [apps.admob.com](https://apps.admob.com/).
2.  **Add App**: Register your Android/iOS app.
3.  **Create Ad Unit**:
    *   Select **Rewarded Ad**.
    *   Set the **Reward amount** to `1`.
    *   Set the **Reward item** to `Credit`.
4.  **Get IDs**:
    *   **App ID**: `ca-app-pub-xxxxxxxxxxxxxxxx~yyyyyyyyyy`
    *   **Ad Unit ID**: `ca-app-pub-xxxxxxxxxxxxxxxx/zzzzzzzzzz`

---

## 2. Frontend Implementation (Mobile)

### A. Load the Ad
In your app (e.g., React Native, Flutter, or Native Android), load the ad when the user opens the "Earn Credits" screen.

```javascript
// Example using React Native AdMob
import { RewardedAd, RewardedAdEventType, TestIds } from 'react-native-google-mobile-ads';

const adUnitId = __DEV__ ? TestIds.REWARDED : 'ca-app-pub-xxxxxxxxxxxxxxxx/zzzzzzzzzz';

const rewardedAd = RewardedAd.createForAdUnit(adUnitId, {
  requestNonPersonalizedAdsOnly: true,
});
```

### B. Handle the Reward
When the user finishes watching, the SDK triggers a callback. **This is where you call the Backend.**

```javascript
rewardedAd.addAdEventListener(RewardedAdEventType.EARNED_REWARD, (reward) => {
  console.log('User earned reward of ', reward);
  
  // Call MagicPic Backend to add the credit
  awardCreditOnBackend();
});
```

### C. Backend API Call
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
        ad_unit_id: "rewarded_ad_main",
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

## 3. Backend details (Already Implemented)

The backend endpoint `/api/rewards/admob` handles:
*   **Daily Limits**: Enforces a limit (Default: 5/day) to prevent botting.
*   **Audit Log**: Saves every ad watch in `ad_watches` table.
*   **Transaction History**: Updates `credit_transactions` so the user knows where the credit came from.
*   **Balance Update**: Directly increments the `credits` column in the `users` table.

---

## 4. Enhanced Security (Optional)

For production, it is highly recommended to enable **Server-Side Verification (SSV)** in the AdMob dashboard.
1.  Enter your callback URL in AdMob: `https://api.magicpic.com/api/rewards/admob-ssv`.
2.  Google will send a POST directly to your server with a digital signature.
3.  This prevents users from "faking" the API call from the frontend.

*Note: If you need SSV implementation, please ask!*
