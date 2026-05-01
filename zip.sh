rm -rf ./zip
mkdir zip

cp proto/kv.proto zip
cp  checkin/controller.py zip
cp check_in_2.md zip

rm -rf check_in_2.zip 
zip -r check_in_2.zip zip