#!/usr/bin/env bash

kubectl.exe apply -f "k8s/storage-service.yaml"
kubectl.exe apply -f "k8s/storage-statefulset.yaml"
kubectl.exe apply -f "k8s/frontend-deployment.yaml"
kubectl.exe apply -f "k8s/frontend-service.yaml"
