<?php 
// pls note that if got an "invalid timestamp" error, 
//it may be caused by wrong timezone setting in php.ini, set it to local one is OK
// print date('Y-m-d H:i:s');
// print date_default_timezone_get();

require_once __DIR__ . '/lib/KdtApiClient.php';

$appId = '7567e92aad02f5a623';
$appSecret = 'fd98abedffdca39a5ac95c228a2bcfae';
$client = new KdtApiClient($appId, $appSecret);


$method = 'kdt.trades.sold.get';
$params = [
	'start_created' => '2015-06-01 00:00:00',
    'page_size' => 2,
	'use_has_next' => true
];

/*
$files = [
	[
		'url' => __DIR__ . '/file1.png',
		'field' => 'images[]',
	],
	[
		'url' => __DIR__ . '/file2.jpg',
		'field' => 'images[]',
	],
];
*/

echo '<pre>';
var_dump( 
	$client->post($method, $params)
);
echo '</pre>';
