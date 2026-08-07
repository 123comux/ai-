import React, { useEffect } from 'react';
import { View, Text, WebView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import styles from './index.module.scss';

const WebviewPage: React.FC = () => {
  const [url, setUrl] = React.useState('');

  useEffect(() => {
    const { url: targetUrl } = Taro.getCurrentInstance().router?.params || {};
    if (targetUrl) {
      setUrl(decodeURIComponent(targetUrl));
    }
  }, []);

  const handleBack = () => {
    Taro.navigateBack();
  };

  return (
    <View className={styles.page}>
      <View className={styles.navBar} onClick={handleBack}>
        <Text className={styles.navBack}>← 返回</Text>
      </View>
      {url ? (
        <WebView className={styles.webview} src={url} />
      ) : (
        <Text className={styles.loadingText}>加载中...</Text>
      )}
    </View>
  );
};

export default WebviewPage;
